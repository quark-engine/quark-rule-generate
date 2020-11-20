
import hashlib


class APIModel:
    def __init__(self, api):
        self.api = api

    @property
    def id(self):
        """
        Return the md5 id of api

        :return: a md5 string of api content
        """
        full_name = str(self.api.method.full_name)
        md5 = hashlib.md5()
        md5.update(full_name.encode("utf-8"))

        return md5.hexdigest()

    @property
    def class_name(self):
        """
        Return class name

        :return: the string of class name
        """
        return str(self.api.method.get_class_name())

    @property
    def method_name(self):
        """
        Return method name

        :return: the string of method name
        """
        return str(self.api.method.get_name())

    @property
    def descriptor(self):
        """
        Return api descriptor

        :return: the string of api descriptor
        """
        return str(self.api.method.get_descriptor())

    @property
    def api_obj(self):
        """
        The object of api

        :return: a dict of api content
        """
        _api = {
            "api_id": self.id,
            "class_name": self.class_name,
            "method_name": self.method_name,
            "descriptor": self.descriptor,
        }
        return _api
