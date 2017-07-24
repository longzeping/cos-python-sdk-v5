# -*- coding=utf-8
from cos_auth import CosS3Auth
from cos_threadpool import SimpleThreadPool
import time
import requests
from os import path
from contextlib import closing
from xml.dom import minidom
import logging
import sys
import os

logger = logging.getLogger(__name__)
fs_coding = sys.getfilesystemencoding()


def to_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return s.decode(fs_coding)


def to_printable_str(s):
    if isinstance(s, unicode):
        return s.encode(fs_coding)
    else:
        return s


def view_bar(num, total):
    ret = 1.0*num / total
    ag = ret * 100
    ab = "\r [%-50s]%.2f%%" % ('='*int(ret*50), ag, )
    sys.stdout.write(ab)
    sys.stdout.flush()


def getTagText(root, tag):
    node = root.getElementsByTagName(tag)[0]
    rc = ""
    for node in node.childNodes:
        if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
            rc = rc + node.data


class CosConfig(object):

    def __init__(self, appid, region, bucket, access_id, access_key, part_size=1, max_thread=5, *args, **kwargs):
        self._appid = appid
        self._region = region
        self._bucket = bucket
        self._access_id = access_id
        self._access_key = access_key
        self._part_size = min(10, part_size)
        self._max_thread = min(10, max_thread)
        logger.info("config parameter-> appid: {appid}, region: {region}, bucket: {bucket}, part_size: {part_size}, max_thread: {max_thread}".format(
                 appid=appid,
                 region=region,
                 bucket=bucket,
                 part_size=part_size,
                 max_thread=max_thread))

    def uri(self, path=None):
        if path:
            url = u"http://{bucket}-{uid}.{region}.myqcloud.com/{path}".format(
                bucket=self._bucket,
                uid=self._appid,
                region=self._region,
                path=to_unicode(path)
            )
        else:
            url = u"http://{bucket}-{uid}.{region}.myqcloud.com".format(
                bucket=self._bucket,
                uid=self._appid,
                region=self._region
            )
        return url


class ObjectInterface(object):

    def __init__(self, conf, session=None):
        self._conf = conf
        self._upload_id = None
        self._headers = []
        self._params = []
        self._md5 = []
        self._retry = 2
        self._file_num = 0
        self._folder_num = 0
        self._have_finished = 0
        if session is None:
            self._session = requests.session()
        else:
            self._session = session


    def put_object(self, Body, Key, **kwargs):
        url = self._conf.uri(path=Key)
        for j in range(self._retry):
            rt = self._session.put(url=url,
                auth=CosS3Auth(self._conf._access_id, self._conf._access_key), data=Body, headers=kwargs['headers'])
            if rt.status_code == 200:
                break
        return rt

    def get_object(self, Key, **kwargs):
        url = self._conf.uri(path=Key)
        for j in range(self._retry):
            rt = self._session.get(url=url, auth=CosS3Auth(self._conf._access_id, self._conf._access_key),headers=kwargs['headers'])
            if rt.status_code == 200:
                break
        return rt

    def delete_object(self, Key, **kwargs):
        url = self._conf.uri(path=Key)
        for j in range(self._retry):
            rt = self._session.delete(url=url, auth=CosS3Auth(self._conf._access_id, self._conf._access_key),headers=kwargs['headers'])
            if rt.status_code == 204:
                break
        return rt


class BucketInterface(object):

    def __init__(self,  conf, session=None):
        self._conf = conf
        self._upload_id = None
        self._md5 = []
        self._have_finished = 0
        self._retry = 2
        if session is None:
            self._session = requests.session()
        else:
            self._session = session

    def put_bucket(self, **kwargs):
        url = self._conf.uri(path='')
        for j in range(self._retry):
            rt = self._session.put(url=url,
                auth=CosS3Auth(self._conf._access_id, self._conf._access_key), headers=kwargs['headers'])
            if rt.status_code == 200:
                break
        return rt

    def delete_bucket(self, Key, **kwargs):
        url = self._conf.uri(path='')
        for j in range(self._retry):
            rt = self._session.delete(url=url, auth=CosS3Auth(self._conf._access_id, self._conf._access_key),headers=kwargs['headers'])
            if rt.status_code == 204:
                break
        return rt


class CosS3Client(object):

    def __init__(self, conf):
        self._conf = conf
        self._session = requests.session()

    def obj_int(self, local_path='', cos_path=''):
        return ObjectInterface(conf=self._conf, session=self._session)

    def buc_int(self):
        return BucketInterface(conf=self._conf, session=self._session)


if __name__ == "__main__":
    pass
