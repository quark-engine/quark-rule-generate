from utils import tools
from quark.Objects.quark import Quark
from db.database import DataBase


class AndroidSampleModel:

    def __init__(self, apk):

        if not self.parse_apk(apk):
            self.parsable = False
            print(self.obj)

        self.db = DataBase()
        self.apk = apk
        self.apk_hash = tools.sha256sum(apk)
        self.parsable = True

        self.db.create_sample_data(self.obj)

    def parse_apk(self, apk):
        """
        Parse apk by androguard.
        :return: failed or succeed
        """
        try:
            self.apk_analysis = Quark(apk)
        except:
            return False
        return True

    @property
    def id(self):
        """
        Return apk_hash

        :return: a string of hashcode sha216
        """
        return self.apk_hash

    @property
    def name(self):
        """
        Return apk filename

        :return: a string of apk filename
        """
        return self.apk_analysis.apkinfo.filename

    @property
    def permissions(self):
        """
        Return a list of permissions usage

        :return: a list of permissions
        """
        if not self.parsable:
            return None
        perm = set(self.apk_analysis.apkinfo.permissions)
        for p in perm.copy():
            if not "android.permission" in p:
                perm.discard(p)
        return list(perm)

    @property
    def apis(self):
        """
        Return a list of APIModel

        :return: a list that consist with APIModel
        """

        if not self.parsable:
            return None

        result = list()
        for cls in self.apk_analysis.apkinfo.analysis.get_external_classes():
            for meth_analysis in cls.get_methods():
                if meth_analysis.is_android_api():
                    result.append(meth_analysis)

        return result

    @property
    def status(self):
        if not self.parsable:
            return None
        return 5

    @property
    def report(self):
        if not self.parsable:
            return None
        return

    @property
    def obj(self):
        """
        The object data for database
        """
        _obj = {
            "_id": self.id,
            "hash": self.id,
            "filename": self.name,
            "parsable": self.parsable,
            "permissions": self.permissions,
            "status": self.status,
            "report": None,
            "api_num": len(self.apis),
            "progress": []
        }
        return _obj
