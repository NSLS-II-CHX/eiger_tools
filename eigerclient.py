"""
class DEigerClient provides an interface to the REST API of jaun

Author: Volker Pilipp
Contact: volker.pilipp@dectris.com
Version: 0.1
Date: 14/02/2014
Copyright See General Terms and Conditions (GTC) on http://www.dectris.com

"""

import os.path
import httplib
import json
import re
import fnmatch

Version = '0.3.27'

##
#  class DEigerClient provides a low level interface to the jaun rest api. You may want to use class DCamera instead.
#
class DEigerClient(object):
    def __init__(self, host = '127.0.0.1', port = 80, verbose = False):
        """
        Create a client object to talk to the restful jaun api.
        Args:
            host: hostname of the detector computer
            port: port usually 80 (http)
            verbose: bool value
        """
        super(DEigerClient,self).__init__()
        self._host = host
        self._port = port
        self._version = Version
        self._verbose = verbose

    def setVerbose(self,verbose):
        """ Switch verbose mode on and off.
        Args:
            verbose: bool value
        """
        self._verbose = verbose

    def version(self,module = 'detector'):
        """Get version of a api module (i.e. 'detector', 'filewriter')
        Args:
            module: 'detector' or 'filewriter'
        """
        return self._request(module,self._version,'GET', url = '/{0}/api/version/'.format(module))

    def listDetectorConfigParams(self):
        """Get list of all detector configuration parameters (param arg of configuration() and setConfiguration()).
        Convenience function, that does detectorConfig(param = 'keys')
        Returns:
            List of parameters.
        """
        return self.detectorConfig('keys')

    def detectorConfig(self,param = None):
        """Get detector configuration parameter
        Args:
            param: query the configuration parameter param, if None get full configuration, if 'keys' get all configuration parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, min, max, allowed_values, unit, value_type and access_mode
        """
        if param is None:
            param = 'keys'
        return self._request('detector','config','GET',parameter = param)

    def setDetectorConfig(self,param,value):
        """
        Set detector configuration parameter param.
        Args:
            param: parameter
            value: value to set
        Returns:
            List of changed parameters.
        """
        data = {'value':value}
        return self._request('detector','config','PUT',parameter = param, data = data)

    def listDetectorCommands(self):
        """
        Get list of all commands that may be sent to Eiger via command().
        Returns:
            List of commands
        """
        return self._request('detector','command','GET',parameter='keys')

    def sendDetectorCommand(self, command):
        """
        Send command to Eiger. The list of all available commands is obtained via listCommands().
        Args:
            command: command to send
        Returns:
            Depending on command None or sequence id.
        """
        return self._request('detector','command','PUT',parameter = command)

    def detectorStatus(self, param = 'keys'):
        """Get detector status information
        Args:
            param: query the status parameter param, if 'keys' get all status parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, value_type, unit, time, state, critical_limits, critical_values
        """
        return self._request('detector','status','GET',parameter = param)


    def fileWriterConfig(self,param = 'keys'):
        """Get filewriter configuration parameter
        Args:
            param: query the configuration parameter param, if 'keys' get all configuration parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, min, max, allowed_values, unit, value_type and access_mode
        """
        return self._request('filewriter','config','GET',parameter = param)

    def setFileWriterConfig(self,param,value):
        """
        Set file writer configuration parameter param.
        Args:
            param: parameter
            value: value to set
        Returns:
            List of changed parameters.
        """
        data = {'value':value}
        return self._request('filewriter','config','PUT',parameter = param, data = data)

    def fileWriterStatus(self,param = 'keys'):
        """Get filewriter status information
        Args:
            param: query the status parameter param, if 'keys' get all status parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, value_type, unit, time, state, critical_limits, critical_values
        """
        return self._request('filewriter','status','GET',parameter = param)

    def fileWriterFiles(self, filename = None, method = 'GET'):
        """
        Obtain file from detector, or delete file.
        Args:
             filename: Name of file on the detector side. If None return list of available files
             method: Eiger 'GET' (get the content of the file) or 'DELETE' (delete file from server)
        Returns:
            List of available files if 'filename' is None,
            else if method is 'GET' the content of the file.
        """
        if filename is None:
            return self._request('filewriter','files','GET')
        else:
            return self._request(None, None, method, parameter = filename, data = None, url = '/data/')

    def fileWriterSave(self,filename,targetDir,regex = False):
        """
        Saves filename in targetDir. If regex is True, filename is considered to be a regular expression.
        Else filename may contain Unix shell-style wildcards. Save all files that match filename.
        Args:
            filename: Name of source file, evtl. regular expression
            targetDir: Directory, where to store the files
        """
        if regex:
            pattern = re.compile(filename)
            [ self.fileWriterSave(f,targetDir)  for f in self.fileWriterFiles() if pattern.match(f) ]
        elif any([ c in filename for c in ['*','?','[',']'] ] ):
            [ self.fileWriterSave(f,targetDir)  for f in self.fileWriterFiles() if fnmatch.fnmatch(f,filename) ]
        else:
            targetPath = os.path.join(targetDir,filename)
            with open(targetPath,'wb') as targetFile:
                self._log('Writing ', targetPath)
                targetFile.write(self.fileWriterFiles(filename))


    def _log(self,*args):
        if self._verbose:
            print ' '.join([ str(elem) for elem in args ])

    def _request(self, module, task, method, parameter = None, data = None, url = None):
        if data is None:
            body = ''
        else:
            body = json.dumps(data)
        headers = {'Accept':'application/json',
                   'Content-type': 'application/json; charset=utf-8'}

        if url is None:
            url = "/{0}/api/{1}/{2}/".format(module,self._version,task)
        if not parameter is None:
            url += '{0}'.format(parameter)

        self._log('sending request to {0}'.format(url))


        connection = httplib.HTTPConnection(self._host,self._port)
        connection.request(method,url, body = body, headers = headers)

        response = connection.getresponse()
        status = response.status
        reason = response.reason
        data = response.read()
        connection.close()
        self._log('Return status: ', status, reason)
        if response.status != 200:
            raise RuntimeError((reason,data))
        try:
            return json.loads(data)
        except ValueError:
            return data




