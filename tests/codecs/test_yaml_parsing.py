#
# CAMP
#
# Copyright (C) 2017, 2018 SINTEF Digital
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#



from camp.codecs import YAMLCodec
from camp.entities.model import DockerFile, DockerImage

from StringIO import StringIO

from unittest import TestCase



class BuiltModelAreComplete(TestCase):


    def setUp(self):
        self._codec = YAMLCodec()


    def test_given_a_one_component_stack(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))

        model = self._codec.load_model_from(StringIO(text))
        self._assert_components(model, ["server"])
        self._assert_services(model, ["Wonderful"])
        self._assert_features(model, [])

        server = model.resolve("server")
        self._assert_component_services(server, ["Wonderful"], [])
        self._assert_component_features(server, [], [])
        self._assert_variables(server, [])

        self._assert_goals(model.goals, ["Wonderful"], [])


    def test_given_a_one_component_stack_with_two_variables(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      variables:\n"
                "        memory:\n"
                "          domain: [1GB, 2GB]\n"
                "        threads:\n"
                "          domain: [64, 128, 256]\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))

        model = self._codec.load_model_from(StringIO(text))
        self._assert_components(model, ["server"])
        self._assert_services(model, ["Wonderful"])
        self._assert_features(model, [])

        server = model.resolve("server")
        self._assert_component_services(server, ["Wonderful"], [])
        self._assert_component_features(server, [], [])
        self._assert_variables(server, [ ("memory", ["1GB", "2GB"]),
                                         ("threads", ["64", "128", "256"])])

        self._assert_goals(model.goals, ["Wonderful"], [])


    def test_given_a_two_component_stack(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      requires_features: [ Python27 ]\n"
                "   python:\n"
                "      provides_features: [ Python27 ]\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        Model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))

        model = self._codec.load_model_from(StringIO(text))
        self._assert_components(model, ["server", "python"])
        self._assert_services(model, ["Wonderful"])
        self._assert_features(model, ["Python27"])

        server = model.resolve("server")
        self._assert_component_services(server, ["Wonderful"], [])
        self._assert_component_features(server, [], ["Python27"])
        self._assert_variables(server, [])

        python = model.resolve("python")
        self._assert_component_services(python, [], [])
        self._assert_component_features(python, ["Python27"], [])
        self._assert_variables(python, [])

        self._assert_goals(model.goals, ["Wonderful"], [])


    def test_given_a_component_with_docker_file(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      implementation:\n"
                "         docker:\n"
                "            file: server/Dockerfile\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings),
                        ([str(w) for w in self._codec.warnings])
        )

        model = self._codec.load_model_from(StringIO(text))
        self._assert_components(model, ["server"])
        self._assert_services(model, ["Wonderful"])
        self._assert_features(model, [])

        server = model.resolve("server")
        self._assert_implementation(server, DockerFile("server/Dockerfile"))
        self._assert_component_services(server, ["Wonderful"], [])
        self._assert_component_features(server, [], [])
        self._assert_variables(server, [])

        self._assert_goals(model.goals, ["Wonderful"], [])


    def test_given_a_component_with_a_docker_image(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      implementation:\n"
                "         docker:\n"
                "            image: fchauvel/camp:dev\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings),
                        ([str(w) for w in self._codec.warnings])
        )

        model = self._codec.load_model_from(StringIO(text))
        self._assert_components(model, ["server"])
        self._assert_services(model, ["Wonderful"])
        self._assert_features(model, [])

        server = model.resolve("server")
        self._assert_implementation(server, DockerImage("fchauvel/camp:dev"))
        self._assert_component_services(server, ["Wonderful"], [])
        self._assert_component_features(server, [], [])
        self._assert_variables(server, [])

        self._assert_goals(model.goals, ["Wonderful"], [])



    def _assert_components(self, model, names):
        self.assertItemsEqual(names,
                              [each.name for each in model.components])


    def _assert_services(self, model, names):
        self.assertItemsEqual(names,
                              [each.name for each in model.services])


    def _assert_features(self, model, names):
        self.assertItemsEqual(names,
                              [each.name for each in model.features])


    def _assert_component_services(self, component, provided, required):
        self.assertItemsEqual(provided,
                              [each.name for each in component.provided_services])
        self.assertItemsEqual(required,
                              [each.name for each in component.required_services])

    def _assert_component_features(self, component, provided, required):
        self.assertItemsEqual(provided,
                              [each.name for each in component.provided_features])
        self.assertItemsEqual(required,
                              [each.name for each in component.required_features])


    def _assert_implementation(self, component, expected_implementation):
        self.assertEqual(expected_implementation,
                         component.implementation)

    def _assert_variables(self, component, variables):
        self.assertEqual(len(variables), len(component.variables))
        for name, values in variables:
            match = next((variable for variable in component.variables\
                          if variable.name == name),
                         None)
            if match:
                self.assertItemsEqual(match.domain, values)

            else:
                self.fail("Component '%s' lacks variable '%s'." % (component.name, name))


    def _assert_goals(self, goal, services, features):
        self.assertItemsEqual(services,
                              [each.name for each in goal.services])
        self.assertItemsEqual(features,
                              [each.name for each in goal.features])



class IgnoredEntriesAreReported(TestCase):

    def setUp(self):
        self._codec = YAMLCodec()


    def test_when_an_extra_entry_is_in_the_root(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "extra: this should not be there!\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(1, len(self._codec.warnings))
        self.assertEqual("extra",
                         self._codec.warnings[0].path)


    def test_when_an_extra_entry_is_in_a_component(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      extra: this should not be there!\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(1, len(self._codec.warnings))
        self.assertEqual("components/server/extra",
                         self._codec.warnings[0].path)


    def test_when_an_extra_entry_is_in_the_implementation(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      implementation:\n"
                "         extra: this should not be there!\n"
                "         docker:\n"
                "            file: DockerFile\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(1, len(self._codec.warnings))
        self.assertEqual("components/server/implementation/extra",
                         self._codec.warnings[0].path)

    def test_when_an_extra_entry_is_in_the_docker(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "      implementation:\n"
                "         docker:\n"
                "            extra: this should not be there!\n"
                "            file: DockerFile\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(1, len(self._codec.warnings))
        self.assertEqual("components/server/implementation/docker/extra",
                         self._codec.warnings[0].path)


    def test_when_an_extra_entry_is_in_the_goals(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Wonderful ]\n"
                "goals:\n"
                "   extra: this should not be there!\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(1, len(self._codec.warnings))
        self.assertEqual("goals/extra",
                         self._codec.warnings[0].path)



class TypeMismatchAreReported(TestCase):


    def setUp(self):
        self._codec = YAMLCodec()


    def test_with_a_string_as_component(self):
        text = ("components: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("dict", "str", "components")


    def test_with_a_string_as_provided_services(self):
        text = ("components: \n"
                "  server:\n"
                "     provides_services: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("list", "str",
                            "components/server/provides_services")


    def test_with_a_string_as_required_services(self):
        text = ("components: \n"
                "  server:\n"
                "     requires_services: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("list", "str",
                            "components/server/requires_services")


    def test_with_a_string_as_provided_features(self):
        text = ("components: \n"
                "  server:\n"
                "     provides_features: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("list", "str",
                            "components/server/provides_features")


    def test_with_a_string_as_required_features(self):
        text = ("components: \n"
                "  server:\n"
                "     requires_features: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("list", "str",
                            "components/server/requires_features")


    def test_with_a_string_as_variables(self):
        text = ("components: \n"
                "  server:\n"
                "     requires_features: [ Awesome ]\n"
                "     variables: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("dict", "str", "components/server/variables")


    def test_with_a_string_as_implementation(self):
        text = ("components: \n"
                "  server:\n"
                "     requires_features: [ Awesome ]\n"
                "     implementation: blablabla\n"
                "goals:\n"
                "   running:\n"
                "      - Wonderful\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("dict", "str", "components/server/implementation")



    def test_with_a_string_as_goals(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Awesome ]\n"
                "goals: blablabla\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("dict", "str", "goals")


    def test_with_a_string_as_running(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Awesome ]\n"
                "goals:\n"
                "  running: blablabla\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assert_warning("list", "str", "goals/running")



    def assert_warning(self, expected, found, path):
        self.assertEqual(1, len(self._codec.warnings),
                         [str(w) for w in self._codec.warnings])
        self.assertEqual(path,
                         self._codec.warnings[0].path)
        self.assertEqual(found,
                         self._codec.warnings[0].found)
        self.assertEqual(expected,
                         self._codec.warnings[0].expected)



class TypeMismatchesAreNotReportedWhenStringIsExpected(TestCase):


    def setUp(self):
        self._codec = YAMLCodec()


    def test_with_a_boolean_among_running_items(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Awesome ]\n"
                "goals:\n"
                "  running: [ Awesome, True ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_provided_services(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_services: [ Awesome, 1234.5 ]\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_required_services(self):
        text = ("components:\n"
                "   server:\n"
                "      requires_services: [ Awesome, 1234.5 ]\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_provided_features(self):
        text = ("components:\n"
                "   server:\n"
                "      provides_features: [ Awesome, 1234.5 ]\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_required_services(self):
        text = ("components:\n"
                "   server:\n"
                "      requires_features: [ Awesome, 1234.5 ]\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_variable_domain(self):
        text = ("components:\n"
                "   server:\n"
                "      requires_services: [ Awesome ]\n"
                "      variables:\n"
                "         memory:\n"
                "           domain: [ High, 1234]\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_docker_file(self):
        text = ("components:\n"
                "   server:\n"
                "      requires_services: [ Awesome ]\n"
                "      implementation:\n"
                "         docker:\n"
                "           file: 1234.5\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))


    def test_with_a_number_among_docker_image(self):
        text = ("components:\n"
                "   server:\n"
                "      requires_services: [ Awesome ]\n"
                "      implementation:\n"
                "         docker:\n"
                "           image: 1234.5\n"
                "goals:\n"
                "  running: [ Awesome ]\n")

        model = self._codec.load_model_from(StringIO(text))

        self.assertEqual(0, len(self._codec.warnings))