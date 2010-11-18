from django import test
from tagstar.models import Fruit
from django.db import transaction

class TagStarTestCase(test.TestCase):

    def setUp(self):
        self.apple = Fruit.objects.create(name='Apple')

    def test_1_update(self):
        tags = self.apple.update_tags("sweet,juicy,round")
        should = ['sweet','juicy','round']

        self.assertEqual(len(tags), len(should))
        self.assertEqual(set(tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))

    def test_2_add(self):
        tags = self.apple.add_tags("red,delicious")
        should = ['red','delicious']
        self.assertEqual(len(tags), len(should))
        self.assertEqual(set(tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))


    def test_3_update_add(self):
        update_tags = self.apple.update_tags("sweet,juicy,round")
        should = ['sweet','juicy','round']

        self.assertEqual(len(update_tags), len(should))
        self.assertEqual(update_tags, should)

        add_tags = self.apple.add_tags("red,delicious")
        should2 = ['red','delicious']
        self.assertEqual(len(add_tags), len(should2))
        self.assertEqual(set(add_tags), set(should2))

        should = should+should2

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))

    def test_4_update(self):
        update_tags = self.apple.update_tags("sweet,juicy,round,round,Round")
        should = ['sweet','juicy','round']

        self.assertEqual(len(update_tags), len(should))
        self.assertEqual(set(update_tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))


    def test_5_add(self):
        add_tags = self.apple.add_tags("red,delicious,Red,red,ReD")
        should = ['red','delicious']

        self.assertEqual(len(add_tags), len(should))
        self.assertEqual(set(add_tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))

    def test_6_add_remove(self):
        add_tags = self.apple.add_tags("red,delicious,Red,red,ReD")

        should = ['red','delicious']

        self.assertEqual(len(add_tags), len(should))
        self.assertEqual(set(add_tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))

        tags = self.apple.remove_tags('red')

        self.assertEqual(len(tags), len(['red']))
        self.assertEqual(set(tags), set(['red']))

        self.assertEqual(len(self.apple.tags_list), len(['delicious']))
        self.assertEqual(set(self.apple.tags_list), set(['delicious']))

    def test_7_add_remove(self):
        add_tags = self.apple.add_tags("red,delicious,Red,red,ReD")

        should = ['red','delicious']

        self.assertEqual(len(add_tags), len(should))
        self.assertEqual(set(add_tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))

        tags = self.apple.remove_tags('red,DoesNotExist')

        self.assertEqual(len(tags), len(['red']))
        self.assertEqual(set(tags), set(['red']))

        self.assertEqual(len(self.apple.tags_list), len(['delicious']))
        self.assertEqual(set(self.apple.tags_list), set(['delicious']))

    def test_8_add_remove(self):
        add_tags = self.apple.add_tags("red,delicious,Red,red,ReD")

        should = ['red','delicious']

        self.assertEqual(len(add_tags), len(should))
        self.assertEqual(set(add_tags), set(should))

        self.assertEqual(len(self.apple.tags_list), len(should))
        self.assertEqual(set(self.apple.tags_list), set(should))

        tags = self.apple.remove_tags('Red')

        self.assertEqual(len(tags), len(['red']))
        self.assertEqual(set(tags), set(['red']))

        self.assertEqual(len(self.apple.tags_list), len(['delicious']))
        self.assertEqual(set(self.apple.tags_list), set(['delicious']))

    def test_9_save(self):
        orange = Fruit(name='orange')
        orange.tags = "sweet,juicy,healthy"
        orange.save()
        should = ['sweet','juicy','healthy']

        self.assertEqual(len(orange.tags_list), len(should))
        self.assertEqual(set(orange.tags_list), set(should))

    def test_9a_save(self):
        orange = Fruit(name='orange')
        orange.tags = "sweet,juicy,healthy,Healthy,HealthY,HeaLthY"
        orange.save()
        should = ['sweet','juicy','healthy']

        self.assertEqual(len(orange.tags_list), len(should))
        self.assertEqual(set(orange.tags_list), set(should))

    def test_10_model_tag(self):
        orange = Fruit(name='orange')
        orange.tags = "sweet,juicy,healthy"
        orange.save()
        should = ['sweet','juicy','healthy']

        self.assertEqual(len(orange.tags_list), len(should))
        self.assertEqual(set(orange.tags_list), set(should))

        ist = [x.name for x in Fruit.objects.get_tags()]

        self.assertEqual(len(ist), len(should))
        self.assertEqual(set(ist), set(should))

    def test_11_tagless(self):
        orange = Fruit.objects.create(name='orange')

        items = [x.name for x in Fruit.objects.get_tagless_items()]
        should = ['Apple','orange']
        self.assertEqual(len(items), len(should))
        self.assertEqual(set(items), set(should))

    def test_11_get_related(self):
        orange = Fruit.objects.create(name='orange')
        cranberry = Fruit.objects.create(name='cranberry')
        orange.add_tags("round")
        self.apple.add_tags("round")
        cranberry.add_tags("round")

        items = [x.name for x in orange.get_related()]
        should = ['Apple','cranberry']
        self.assertEqual(len(items), len(should))
        self.assertEqual(set(items), set(should))


    def test_12_tag_count(self):
        orange = Fruit.objects.create(name='orange')
        cranberry = Fruit.objects.create(name='cranberry')
        orange.add_tags("round")
        self.apple.add_tags("round")
        cranberry.add_tags("round")

        tags = [(x.name,x.count) for x in orange.get_tags()]

        should = [('round',3)]
        self.assertEqual(len(tags), len(should))
        self.assertEqual(set(tags), set(should))

    def test_13_tag_count_delete(self):
        orange = Fruit.objects.create(name='orange')
        cranberry = Fruit.objects.create(name='cranberry')
        orange.add_tags("round")
        self.apple.add_tags("round")
        cranberry.add_tags("round")
        cranberry.remove_tags('round')

        tags = [(x.name,x.count) for x in orange.get_tags()]

        should = [('round',2)]
        self.assertEqual(len(tags), len(should))
        self.assertEqual(set(tags), set(should))

    def test_14_final(self):
        orange = Fruit.objects.create(name='orange')
        cranberry = Fruit.objects.create(name='cranberry')

        orange.add_tags("round")
        self.apple.add_tags("round")
        cranberry.add_tags("round")

        cranberry.remove_tags('round')

        cranberry.update_tags("round,red")

        cranberry.add_tags("berry")
        orange.add_tags("yellow")
        self.apple.add_tags("red")

        tags = [(x.name,x.count) for x in orange.get_tags()]

        should = [('round',3), ('yellow',1)]
        self.assertEqual(len(tags), len(should))
        self.assertEqual(set(tags), set(should))