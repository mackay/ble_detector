from datetime import datetime
from core.system import SystemBase


class Entity(SystemBase):

    def __init__(self, uuid, entity_model_cls):
        super(Entity, self).__init__()
        self.uuid = uuid
        self.entity_model_cls = entity_model_cls

    def get(self):
        return self.entity_model_cls.get(self.entity_model_cls.uuid == self.uuid)


class EntityAgent(Entity):

    def __init__(self, uuid, entity_model_cls):
        super(EntityAgent, self).__init__(uuid, entity_model_cls)

    def checkin(self, status_dictionary=None):
        query = self.entity_model_cls.select().where(self.entity_model_cls.uuid == self.uuid)

        #if not in DB, create
        if not query.exists():
            entity = self.entity_model_cls.create( uuid=self.uuid )
        else:
            entity = query.limit(1)[0]

        #update DB data
        entity.last_active = datetime.utcnow()
        entity.save()
        return entity

    def increment_packet_count(self):
        entity = self.get()
        entity.total_packets += 1
        entity.save()

    def reset_packet_count(self):
        entity = self.get()
        entity.total_packets = 0
        entity.save()

    def clear_entities(self):
        return self.entity_model_cls.delete().execute()
