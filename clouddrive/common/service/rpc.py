'''
    OneDrive for Kodi
    Copyright (C) 2015 - Carlos Guzman

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    Created on Mar 1, 2015
    @author: Carlos Guzman (cguZZman) carlosguzmang@hotmail.com
'''

import inspect

from clouddrive.common.ui.logger import Logger
from clouddrive.common.service.base import BaseService, BaseHandler
from clouddrive.common.utils import Utils
from clouddrive.common.exception import ExceptionUtils
from urllib2 import HTTPError

class RpcService(BaseService):
    name = 'rpc'
    def __init__(self, listener):
        super(RpcService, self).__init__(listener)
        self._handler = RpcHandler
    
class RpcHandler(BaseHandler):
    def do_POST(self):
        content = Utils.get_file_buffer()
        try:
            size = int(self.headers.getheader('content-length', 0))
            cmd = eval(self.rfile.read(size))
            method = Utils.get_safe_value(cmd, 'method')
            if method:
                code = 200
                args = Utils.get_safe_value(cmd, 'args', [])
                kwargs = Utils.get_safe_value(cmd, 'kwargs', {})
                Logger.debug('Command received:\n%s' % cmd)
                content.write(repr(self.server.data.rpc(method, args, kwargs)))
            else:
                code = 400
                content.write('Method required')
        except Exception as e:
            httpex = ExceptionUtils.extract_exception(e, HTTPError)
            if httpex:
                code = httpex.code
            else:
                code = 500
            content.write(ExceptionUtils.full_stacktrace(e))
        self.write_response(code, content=content)
        

class RemoteProcessCallable(object):
 
    def rpc(self, method, args=[], kwargs={}):
        method = getattr(self, method)
        fkwargs = {}
        for name in inspect.getargspec(method)[0]:
            if name in kwargs:
                fkwargs[name] = kwargs[name]
        return method(*args, **fkwargs)
    
    '''
    def on_execute_method(self, exec_id, method, args='[]', kwargs='{}'):
        Logger.notice('now on_execute_method %s...' % method)
        home_window = KodiUtils.get_window(10000)
        key = '%s-%s' % (self._addonid, exec_id)
        status_key = '%s.status' % key
        result_key = '%s.result' % key
        try:
            home_window.setProperty(status_key, 'in-progress')
            args = eval(args)
            kwargs = eval(kwargs)
            method = getattr(self, method)
            fkwargs = {}
            for name in inspect.getargspec(method)[0]:
                if name in kwargs:
                    fkwargs[name] = kwargs[name]
            home_window.setProperty(result_key, repr(method(*args, **fkwargs)))
            home_window.setProperty(status_key, 'success')
        except Exception as e:
            home_window.setProperty(result_key, repr(e))
            home_window.setProperty(status_key, 'fail')
            raise e
    '''
        