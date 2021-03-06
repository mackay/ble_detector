
from core.system import SystemBase
from core.activity import BeaconActivity
from core.models import Signal, Beacon, Detector
from core.models import Training, TrainingSignal
from datetime import datetime, timedelta

from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

import pickle
import json

import io
import csv

import logging
log = logging.getLogger()


class TrainingActivity(SystemBase):

    def __init__(self):
        super(SystemBase, self).__init__()

    def get_training_expectation(self):
        return json.loads( self.get_option(SystemBase.TRAINING_KEY) )

    def add(self, beacon_uuid, stale_signal_limit=5, expectation=None, max_beacons=1):
        expectation = expectation or self.get_training_expectation()

        beacon = BeaconActivity(beacon_uuid).get()
        signal_slice = BeaconActivity(beacon_uuid).get_signal_slice(stale_time_ms=1000*stale_signal_limit)

        #if there aren't enough signals, skip
        if len(signal_slice) < max_beacons:
            return None

        #create the training set if we have enough data
        training = Training.create( beacon=beacon, expectation=expectation )
        for signal in signal_slice:
            TrainingSignal.create(training=training, signal=signal)

        return training

    def get_signals(self, training):
        return [training_signal_link.signal for training_signal_link in training.signals]

    def normalize_signals_dbm(self, rssi_list, db_floor=-90.0):
        rssi_list = [ max( float(rssi), db_floor) for rssi in rssi_list ]
        max_rssi = max(rssi_list)

        return [ ( rssi - db_floor) / ( max_rssi - db_floor ) for rssi in rssi_list ]
        # return [ ( max_rssi - db_floor) / ( float(rssi) - db_floor ) for rssi in rssi_list ]

    def normalize_signals_mw(self, rssi_list):
        rssi_list = [ pow(10, (rssi/10)) for rssi in rssi_list ]
        max_rssi = float( max(rssi_list) )

        return [ float(rssi) / max_rssi for rssi in rssi_list ]


class ClassifierBase(object):

    def __init__(self):
        pass

    def get_detector_sequence(self):
        sequence = [ detector.uuid for detector in Detector.select() ]
        return sequence


class Trainer(ClassifierBase):

    @classmethod
    def __default_value_fn(cls, training_entry, signal, signal_index):
        return training_entry._data["normalized_dbm"][signal_index]["rssi"]

    @classmethod
    def clear_training(cls):
        signal_removal_count = TrainingSignal.delete().execute()
        Training.delete().execute()

        return signal_removal_count

    def __init__(self):
        super(Trainer, self).__init__()
        self.networks = None

    def get_training_data(self):
        training_set = [ ]

        for training_item in Training.select().where(Training.is_used == 1):
            self.enrich_training_model(training_item)

            training_set.append(training_item)

        return training_set

    def enrich_training_model(self, training):
        training._data["signals"] = TrainingActivity().get_signals( training )
        training._data["normalized_dbm"] = [ ]
        training._data["normalized_mw"] = [ ]

        normalized_signals_dbm = TrainingActivity().normalize_signals_dbm( [ signal.rssi for signal in training._data["signals"] ] )
        normalized_signals_mw = TrainingActivity().normalize_signals_mw( [ signal.rssi for signal in training._data["signals"] ] )

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

    def get_training_slices(self, value_fn=None, detector_sequence=None):
        value_fn = value_fn or Trainer.__default_value_fn
        detector_sequence = detector_sequence or self.get_detector_sequence()
        slices = [ ]

        for training_entry in self.get_training_data():
            training_slice = { "date": training_entry.date,
                               "expectation": training_entry.expectation,
                               "beacon": training_entry.beacon.uuid,
                               "signals": { },
                               "values": [ ],
                               "entry": training_entry }

            for idx, signal in enumerate( training_entry._data["signals"] ):
                training_slice["signals"][signal.detector.uuid] = value_fn(training_entry, signal, idx)

            for detector_uuid in detector_sequence:
                if detector_uuid in training_slice["signals"]:
                    training_slice["values"].append( training_slice["signals"][detector_uuid] )
                else:
                    training_slice["values"].append( 0 )

            slices.append(training_slice)

        return slices

    def _get_dimensions(self, training_slices):
        dimensions = set({})

        for training_slice in training_slices:
            for key in training_slice["expectation"]:
                dimensions.add(key)

        return list(dimensions)

    def _filter_slices_to_dimension(self, training_slices, dimension):
        return [ training_slice for training_slice in training_slices if dimension in training_slice["expectation"] ]

    def train(self):
        networks = [ ]

        training_slices = self.get_training_slices()
        for dimension in self._get_dimensions(training_slices):
            dimension_training_slices = self._filter_slices_to_dimension(training_slices, dimension)

            input_set = [ _slice["values"] for _slice in dimension_training_slices ]
            output_set = [ _slice["expectation"][dimension] for _slice in dimension_training_slices ]

            if "_regression" in dimension:
                network_class = MLPRegressor
                hidden_layer_sizes = (20 * len(input_set[0]),) * len(input_set[0])
            else:
                network_class = MLPClassifier

                unique_outputs = set([ output for output in output_set ])
                hidden_layer_sizes = (25 + len(unique_outputs), ) * len(input_set[0])

            network = network_class( solver='lbfgs',
                                     alpha=1e-5,
                                     hidden_layer_sizes=hidden_layer_sizes,
                                     random_state=1,
                                     max_iter=10000)

            if log.getEffectiveLevel() <= logging.DEBUG:
                for idx, input_data in enumerate(input_set):
                    log.debug( str(dimension_training_slices[idx]["entry"].id) + " :: " + output_set[idx] + " :: " + str(input_data) )

            network.fit(input_set, output_set)

            if log.getEffectiveLevel() <= logging.DEBUG:

                alt_input_set, alt_input_test, alt_output_set, alt_output_test = train_test_split(input_set, output_set)
                predictions = network.predict(alt_input_test)

                log.debug("Sampled subset")
                log.debug( "\n" + str(confusion_matrix(alt_output_test, predictions)) )
                log.debug( "\n" + str(classification_report(alt_output_test, predictions)) )

                predictions = network.predict(input_set)
                log.debug("Full dataset")
                log.debug( "\n" + str(confusion_matrix(output_set, predictions)) )
                log.debug( "\n" + str(classification_report(output_set, predictions)) )

            networks.append( Network(dimension, network) )

        return networks


class Network(ClassifierBase):

    def __init__(self, dimension, trained_network):
        super(Network, self).__init__()
        self.dimension = dimension
        self.network = trained_network

    def predict(self, signals, detector_sequence=None):
        detector_sequence = detector_sequence or self.get_detector_sequence()

        normalized_signals_dbm = TrainingActivity().normalize_signals_dbm( [ signal.rssi for signal in signals ] )
        signal_map = { signal.detector.uuid: normalized_signals_dbm[idx] for idx, signal in enumerate(signals) }

        values = [ ]
        for detector_uuid in detector_sequence:
            if detector_uuid in signal_map:
                values.append( signal_map[detector_uuid] )
            else:
                values.append( 0 )

        if log.getEffectiveLevel() <= logging.DEBUG:
            log.debug(str(values))
            log.debug(str(detector_sequence))

            if isinstance(self.network, MLPClassifier):
                log.debug(str(self.network.predict_proba([values])))

        return self.network.predict([values])[0]
