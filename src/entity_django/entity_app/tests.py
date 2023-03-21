from django.test import TestCase
from entity_app.models import *
class Tests(TestCase):
    def create_testdoc(self):
        test_doc = Document()
        test_doc.filename = "test_name.html.gz"
        test_doc.text = "this the the document text"
        test_doc.save()
        return test_doc

    def create_testent(self):
        test_ent = Entity()
        test_ent.entityID = "www.test.co.uk"
        test_ent.text = "test"
        test_ent.abstract = "this is a test entity"
        test_ent.sensitivity = 3
        test_ent.slug = "test"
        test_ent.save()
        return test_ent

    def create_testinst(self):
        test_inst = Instance()
        test_inst.documentID = self.create_testdoc()
        test_inst.entityID = self.create_testent()
        test_inst.start=1
        test_inst.stop=2
        test_inst.save()
        return test_inst

    def create_testtopicword(self):
        test_topicword = TopicWord()
        test_topicword.entityID = self.create_testent()
        test_topicword.topicNumber = 1
        test_topicword.weight = 0.5
        test_topicword.save()
        return test_topicword

    def create_testtopicdoc(self):
        test_topicdoc = TopicDocument()
        test_topicdoc.documentID = self.create_testdoc()
        test_topicdoc.topicNumber = 1
        test_topicdoc.weight = 0.5
        test_topicdoc.save()
        return test_topicdoc


    def testcreate_document(self):
        test_doc = self.create_testdoc()
        retr_doc = Document.objects.get(filename=test_doc.filename)
        self.assertEqual(test_doc,retr_doc)

    def testcreate_entity(self):
        test_ent = self.create_testent()
        retr_ent = Entity.objects.get(entityID=test_ent.entityID)
        self.assertEqual(test_ent,retr_ent)

    def testcreate_instance(self):
        test_inst = self.create_testinst()
        retr_inst = Instance.objects.get(entityID=test_inst.entityID, documentID=test_inst.documentID)
        self.assertEqual(test_inst,retr_inst)

    def testcreate_topicword(self):
        test_topicword = self.create_testtopicword()
        retr_topicword = TopicWord.objects.get(entityID=test_topicword.entityID)
        self.assertEqual(test_topicword,retr_topicword)

    def testcreate_topicdoc(self):
        test_topicdoc = self.create_testtopicdoc()
        retr_topicdoc = TopicDocument.objects.get(documentID=test_topicdoc.documentID)
        self.assertEqual(test_topicdoc,retr_topicdoc)

    def testdelete_topicdoc(self):
        TopicDocument.objects.all().delete()
        topicdocs = list(TopicDocument.objects.all())
        self.assertEqual(topicdocs,[])

    def testdelete_topicword(self):
        TopicWord.objects.all().delete()
        topicwords = list(TopicWord.objects.all())
        self.assertEqual(topicwords,[])

    def testdelete_instance(self):
        Instance.objects.all().delete()
        insts = list(Instance.objects.all())
        self.assertEqual(insts,[])

    def testdelete_entity(self):
        Entity.objects.all().delete()
        ents = list(Entity.objects.all())
        self.assertEqual(ents,[])

    def testdelete_document(self):
        Document.objects.all().delete()
        docs = list(Document.objects.all())
        self.assertEqual(docs,[])

    def testent_cascade(self):
        test_inst = self.create_testinst()
        test_ent = test_inst.entityID
        test_ent.delete()
        insts = list(Instance.objects.all())
        self.assertEqual(insts,[])

    def testdoc_cascade(self):
        test_inst = self.create_testinst()
        test_doc = test_inst.documentID
        test_doc.delete()
        insts = list(Instance.objects.all())
        self.assertEqual(insts,[])

    def testtopicword_cascade(self):
        test_topicword = self.create_testtopicword()
        test_ent = test_topicword.entityID
        test_ent.delete()
        topicwords = list(TopicWord.objects.all())
        self.assertEqual(topicwords,[])

    def testtopicdoc_cascade(self):
        test_topicdoc = self.create_testtopicdoc()
        test_doc = test_topicdoc.documentID
        test_doc.delete()
        topicdocs = list(TopicDocument.objects.all())
        self.assertEqual(topicdocs,[])






