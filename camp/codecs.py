#
# CAMP
#
# Copyright (C) 2017, 2018 SINTEF Digital
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#


from camp.entities.model import Model, Component, Service, Goals, Variable, \
    Feature, DockerFile, DockerImage

from yaml import load, dump as yaml_dump



class YAMLCodec(object):


    def __init__(self):
        self._warnings = []


    def save_configuration(self, configuration, stream):
        dictionary = self._as_dictionary(configuration)
        yaml_dump(dictionary, stream, default_flow_style=False)

    def _as_dictionary(self, configuration):
        dictionary = {}
        dictionary["instances"] = []
        for each_instance in configuration.instances:
            instance = {}
            instance["name"] = each_instance.name
            instance["definition"] = each_instance.definition.name
            instance["feature_provider"] = each_instance.feature_provider
            instance["service_providers"] = [ each.name \
                                              for each in each_instance.service_providers]
            instance["configuration"] = {}
            for variable, value in each_instance.configuration:
                instance["configuration"][variable.name] = value
                
            dictionary["instances"].append(instance)
        return dictionary
    

    def load_model_from(self, stream):
        data = load(stream)
        components = []
        goals = Goals()
        for key, item in data.items():
            if key == Keys.COMPONENTS:
                if type(item) != dict:
                    self._wrong_type(dict, type(item), key)
                    continue
                components = self._parse_components(item)
            elif key == Keys.GOALS:
                if type(item) != dict:
                    self._wrong_type(dict, type(item), key)
                    continue
                goals = self._parse_goals(item)
            else:
                self._ignore(key)
        return Model(components, goals)


    def _parse_components(self, data):
        components = []
        for key, item in data.items():
            components.append(self._parse_component(key, item))
        return components


    def _parse_component(self, name, data):
        provided_services = []
        required_services = []
        provided_features = []
        required_features = []
        variables = []
        implementation = None

        for key, item in data.items():

            if key == Keys.PROVIDES_SERVICES:
                if type(item) != list:
                    self._wrong_type(list, type(item), Keys.COMPONENTS, name, key)
                    continue
                for each_name in item:
                    provided_services.append(Service(self._escape(each_name)))

            elif key == Keys.REQUIRES_SERVICES:
                if type(item) != list:
                    self._wrong_type(list, type(item), Keys.COMPONENTS, name, key)
                    continue
                for each_name in item:
                    required_services.append(Service(self._escape(each_name)))

            elif key == Keys.PROVIDES_FEATURES:
                if type(item) != list:
                    self._wrong_type(list, type(item), Keys.COMPONENTS, name, key)
                    continue
                for each_name in item:
                    provided_features.append(Feature(self._escape(each_name)))

            elif key == Keys.REQUIRES_FEATURES:
                if type(item) != list:
                    self._wrong_type(list, type(item), Keys.COMPONENTS, name, key)
                    continue
                for each_name in item:
                    required_features.append(Feature(self._escape(each_name)))

            elif key == Keys.VARIABLES:
                if type(item) != dict:
                    self._wrong_type(dict, type(item), Keys.COMPONENTS, name, key)
                    continue
                variables = self._parse_variables(item)

            elif key == Keys.IMPLEMENTATION:
                if type(item) != dict:
                    self._wrong_type(dict, type(item), Keys.COMPONENTS, name, key)
                    continue
                implementation = self._parse_implementation(name, item)
                
            else:
                self._ignore(Keys.COMPONENTS, name, key)


        return Component(name,
                         provided_services=provided_services,
                         required_services=required_services,
                         provided_features=provided_features,
                         required_features=required_features,
                         variables=variables,
                         implementation=implementation)

    def _escape(self, name):
        if type(name) is not str:
            return "_" + str(name)
        return name

    def _parse_variables(self, data):
        variables = []
        for key, item in data.items():
            variables.append(self._parse_variable(key, item))
        return variables


    def _parse_variable(self, name, data):
        domain = []
        if Keys.DOMAIN in data:
            for each_value in data[Keys.DOMAIN]:
                domain.append(str(each_value))
        return Variable(name, domain)


    def _parse_implementation(self, name, data):
        implementation = None
        for key, item in data.items():
            if key == Keys.DOCKER:
                implementation = self._parse_docker(name, item)
            else:
                self._ignore(Keys.COMPONENTS, name, Keys.IMPLEMENTATION, key)
        return implementation


    def _parse_docker(self, name, data):
        docker = None
        for key, item in data.items():
            if key == Keys.FILE:
                docker = DockerFile(self._escape(item))
            elif key == Keys.IMAGE:
                docker = DockerImage(self._escape(item))
            else:
                self._ignore(Keys.COMPONENTS, name, Keys.IMPLEMENTATION, Keys.DOCKER, key)
        return docker


    def _parse_goals(self, data):
        running_services = []
        for key, item in data.items():
            if key == Keys.RUNNING:
                if type(item) != list:
                    self._wrong_type(list, type(item), Keys.GOALS, key)
                    continue
                for index, each_name in enumerate(item, 1):
                    running_services.append(Service(str(each_name)))
            else:
                self._ignore(Keys.GOALS, key)
                
        return Goals(running_services)


    def _ignore(self, *path):
        self._warnings.append(IgnoredEntry(*path))


    def _wrong_type(self, expected, found, *path):
        self._warnings.append(WrongType(expected, found, *path))


    @property
    def warnings(self):
        return self._warnings



class Keys:
    """
    The labels that are fixed in the YAML
    """
    
    COMPONENTS = "components"
    DOCKER = "docker"
    DOMAIN = "domain"
    FILE = "file"
    GOALS = "goals"
    IMAGE = "image"
    IMPLEMENTATION = "implementation"
    PROVIDES_FEATURES = "provides_features"
    PROVIDES_SERVICES = "provides_services"
    REQUIRES_FEATURES = "requires_features"
    REQUIRES_SERVICES = "requires_services"
    RUNNING = "running"
    VARIABLES = "variables"



class Warning(object):

    def __init__(self, *path):
        self._path = "/".join(path)


    @property
    def path(self):
        return self._path
    


class IgnoredEntry(Warning):

    def __init__(self, *path):
        super(IgnoredEntry, self).__init__(*path)

    def __str__(self):
        return "Entry '%s' ignored!" % self._path


    
class WrongType(Warning):

    def __init__(self, expected, found, *path):
        super(WrongType, self).__init__(*path)
        self._expected = expected.__name__
        self._found = found.__name__

    @property
    def found(self):
        return self._found


    @property
    def expected(self):
        return self._expected


    def __str__(self):
        return "Wrong type at '%s'! Expected '%s' but found '%s'." % (self._path,
                                                                  self._expected,
                                                                  self._found)

    