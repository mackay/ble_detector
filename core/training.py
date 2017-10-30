
from core.system import SystemBase
from core.beacon import BeaconAgent
from core.models import Signal, Beacon
from core.models import Training, TrainingSignal
from datetime import datetime, timedelta

import json

import io
import csv


class TrainingAgent(SystemBase):

    def __init__(self):
        super(SystemBase, self).__init__()

    def get_training_expectation(self):
        return json.loads( self.get_option(SystemBase.TRAINING_KEY) )

    def add(self, beacon_uuid, stale_signal_limit=5, expectation=None):

        expectation = expectation or self.get_training_expectation()

        beacon = BeaconAgent(beacon_uuid).get()
        stale_cutoff_date = datetime.utcnow() - timedelta(seconds=stale_signal_limit)

        query = ( Signal.select()
                        .join(Beacon, on=(Beacon.id == Signal.beacon))
                        .where(Beacon.uuid == beacon_uuid)
                        .group_by(Signal.beacon, Signal.detector)
                        .order_by(Signal.date) )

        #get all signals realted to the beacon younger than the stale counter
        #group them by detector
        #get the newest of each
        query = ( Signal.select()
                        .join(Beacon, on=(Beacon.id == Signal.beacon))
                        .where(Beacon.uuid == beacon_uuid)
                        .where(Signal.date > stale_cutoff_date)
                        .group_by(Signal.beacon, Signal.detector)
                        .order_by(Signal.date) )

        #if there aren't enough signals, skip
        if query.count() < 3:
            return None

        #create the training set if we have enough data
        training = Training.create( beacon=beacon, expectation=expectation )
        for signal in query:
            TrainingSignal.create(training=training, signal=signal)

        return training

    def get_signals(self, training):
        return [training_signal_link.signal for training_signal_link in training.signals]

    def normalize_signals_dbm(self, rssi_list):
        rssi_list = [ rssi for rssi in rssi_list ]
        max_rssi = float( max(rssi_list) )

        return [ max_rssi / float(rssi) for rssi in rssi_list ]

    def normalize_signals_mw(self, rssi_list):
        rssi_list = [ pow(10, (rssi/10)) for rssi in rssi_list ]
        max_rssi = float( max(rssi_list) )

        return [ float(rssi) / max_rssi for rssi in rssi_list ]


class TrainingNetwork(object):

    @classmethod
    def clear_training(cls):
        signal_removal_count = TrainingSignal.delete().execute()
        Training.delete().execute()

        return signal_removal_count

    def __init__(self):
        pass

    def get_training_data(self):
        training_set = [ ]

        for training_item in Training.select():
            self.enrich_training_model(training_item)

            training_set.append(training_item)

        return training_set

    def enrich_training_model(self, training):
        training._data["signals"] = TrainingAgent().get_signals( training )
        training._data["normalized_dbm"] = [ ]
        training._data["normalized_mw"] = [ ]

        normalized_signals_dbm = TrainingAgent().normalize_signals_dbm( [ signal.rssi for signal in training._data["signals"] ] )
        normalized_signals_mw = TrainingAgent().normalize_signals_mw( [ signal.rssi for signal in training._data["signals"] ] )
        for idx, signal in enumerate( training._data["signals"] ):
            training._data["normalized_dbm"].append({
                "beacon": signal._data["beacon"],
                "rssi": normalized_signals_dbm[idx]
            })
            training._data["normalized_mw"].append({
                "beacon": signal._data["beacon"],
                "rssi": normalized_signals_mw[idx]
            })

        return training

    def get_training_csv(self):
        output = io.BytesIO()
        writer = csv.writer(output)

        header_row = [ "Training Set", "Date", "Beacon", "Expectation", "Detector", "RSSI", "Normalied dBm", "Normalied mW"]
        writer.writerow( header_row )

        for training_entry in self.get_training_data():

            for idx, signal in enumerate( training_entry._data["signals"] ):
                csv_row = [ training_entry.id,
                            training_entry.date,
                            training_entry.beacon.uuid,
                            training_entry.expectation,
                            signal.detector.uuid,
                            signal.rssi,
                            training_entry._data["normalized_dbm"][idx]["rssi"],
                            training_entry._data["normalized_mw"][idx]["rssi"] ]

                writer.writerow( csv_row )

        return output.getvalue()

    def build_network(self):
        pass
