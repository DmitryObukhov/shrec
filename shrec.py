#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function
import argparse
import getpass
from shellwrapper import ShellWrapper

__author__ = 'dmitry.obukhov'

'''
#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function
from textprocessor import TextProcessor
from batchprocessor import BatchProcessor

class ShellRecipes(object):
    """ Shell interface """

    def __init__(self, debug=False, quiet=True, log_file=""):
        """ Class Constructor """
        self.debug = debug
        self.quiet = quiet
        self.batch = BatchProcessor(self.debug, self.quiet, "auto")
    #--

    def match_os(self, required_os):
        """ Enable root login to SSH server """
        if self.batch.system != required_os: # Check the current platform
            self.batch.prn("Current platform is %s" % batch.system)
            self.batch.prn("Command is supported only for %s platforms, terminating" % required_os)
            self.batch.prn("See details in %s" % batch.LogFile)
            self.batch.exit(0)
        #---
        return True
    #---

    def enable_root_ssh():
        """ Enable root login to SSH server """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---
        batch.replace_line_in_file('/etc/ssh/sshd_config', \
            'PermitRootLogin', \
            'PermitRootLogin yes')
        batch.run('service sshd restart')
        return batch.error_count
    #---

    def disable_root_ssh():
        """ Disable root login to SSH server """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---
        batch.replace_line_in_file('/etc/ssh/sshd_config', \
            'PermitRootLogin', \
            'PermitRootLogin without-password')
        #---
        batch.run('service sshd restart')
        return batch.error_count
    #---

    def enable_tcg():
        """ Enable access to SED (TCG) storage """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---

        # Normal operation
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
        # run update-grub

        return batch.error_count
    #---

    def set_hostname():
        """ Disable root login to SSH server """
        if not self.match_os('Linux'): # Check the current platform
            return -1
        #---

        # Normal operation
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
        # run update-grub
        while True:
            new_host_name = ''
            if args.naming == 'mac':
                new_host_name = batch.get_mac_address('').upper()
            elif args.naming == 'rnd':
                new_host_name = TextProcessor.random_string(8)
            else:
                batch.prn("ERROR: Unsupported naming scheme %s" % args.naming)
                break
            #---

            if new_host_name == '':
                batch.prn("ERROR: Cannot get new hostname.")
                break
            #---

            batch.run('hostname %s' % new_host_name, silent=True)
            if batch.cret != 0:
                batch.prn("ERROR: Command execution error.")
                break
            #---


            if not batch.write_file('/etc/hostname', [new_host_name]):
                batch.prn("ERROR: writing /etc/hostname")
                break
            #---


            #-------------------- SUCCESS
            exit_code = 0
            break
        #---

        return batch.error_count
    #---

#--- end of class ShellRecipes


'''


def main():
    """ main function to parse arguments """
    exit_code = -1
    parser = argparse.ArgumentParser(description="Shell Receipes Engine", formatter_class=argparse.RawDescriptionHelpFormatter)
    # Global arguments
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")

    subparsers = parser.add_subparsers(help='Supported commands', dest='command')

    setup_parser = subparsers.add_parser('setup', help='Setup Python module')
    install_parser = subparsers.add_parser('install', help='Install shrec as system utility')
    template_parser = subparsers.add_parser('template', help='Install shrec as system utility')
    template_parser.add_argument('script', action='store', nargs='?', default='', help='Template file')

    args = parser.parse_args()

    if args.command == 'setup':
        batch = ShellWrapper(args.debug, args.quiet, "auto")
        setup_script = [ \
                "#!/usr/bin/env python", \
                "from distutils.core import setup", \
                "setup(name='shrellwrapper',version='0.3',", \
                "      description='Script Helper',", \
                "      py_modules=['shrellwrapper'])", \
                "" \
            ]
        #---
        batch.save(setup_script, 'temp_setup.py')
        batch.run('python temp_setup.py install')
        batch.remove('temp_setup.py')
        batch.prntxt(batch.cout, '', '-- installation log --')
        batch.exit(0)
    #--

    if args.command == 'install':
        # todo: installation, copy list of scripts to /usr/local/bin
        pass
    #--

    if args.command == 'template':
        batch = ShellWrapper(args.debug, args.quiet, "auto")
        template_script = [ \
                "#!/usr/bin/env python", \
                '""" SHell RECipe: """', \
                'from __future__ import print_function', \
                'import argparse', \
                "from shellwrapper import ShellWrapper", \
                '__author__ = "%s"' % getpass.getuser(), \
                '', \
                'def main():', \
                '    """ main function """', \
                '    parser = argparse.ArgumentParser(description="Shell Receipe", formatter_class=argparse.RawDescriptionHelpFormatter)', \
                '    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")', \
                '    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")', \
                '    args = parser.parse_args()', \
                '', \
                '    # Create shell wrapper and perform necessary commands', \
                '    batch = ShellWrapper(args.debug, args.quiet, "auto")', \
                '    # put your code here. For example, batch.run("ping 127.0.0.1")', \
                '    batch.exit(0) # batch.exit terminates the script', \
                '#---', \
                '', \
                'if __name__ == "__main__":', \
                '    main()', \
                '#---', \
                "" \
            ]
        #---
        if args.script == '':
            batch.prntxt(template_script)
        else:
            batch.save(template_script, args.script)
        #---
        batch.exit()
    #--



    print("Unhandled command %s" % args.command)
    return -1
#---


if __name__ == "__main__":
    exit(main())
#---
