from datetime import datetime


class EntityProcess(object):

    def __init__(self, uuid, entity_model_cls):
        self.uuid = uuid
        self.entity_model_cls = entity_model_cls


    def get(self):
        return self.entity_model_cls.get(self.entity_model_cls.uuid == self.uuid)

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
