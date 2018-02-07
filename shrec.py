#!/usr/bin/python
""" SHell RECipes module """
from __future__ import print_function
import argparse
from shellwrapper import ShellWrapper

__author__ = 'dmitry.obukhov'


def install_script(shw,script,script_dir='/opt'):
    """ Copy script to location (/opt) and chmod it for execution """
    sname = shw.fname_name(script)
    shw.run('cp %s %s/%s' % (script,script_dir,sname))
    shw.run('chmod +x %s/%s' % (script_dir,sname))
    pass
#---

def feature_rootssh(shw,enable):
    """ Enable/Disable root login to SSH server """
    if not shw.match_os('Linux'): # Check the current platform
        return False
    #---
    if enable:
        shw.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin yes')
    else:
        shw.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin without-password')
    #---
    shw.run('service sshd restart')
    return batch.error_count
#---


def feature_tcg(shw,enable):
    """ Enable/Disable root login to SSH server """
    if not shw.match_os('Linux'): # Check the current platform
        return False
    #---
    if enable:
        # Normal operation
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
        # run update-grub
        # shw.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin yes')
        pass
    else:
        pass
        #shw.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin without-password')
    #---
    shw.run('service sshd restart')
    return batch.error_count
#---


def install_java(shw,enable):
    """ Enable/Disable root login to SSH server """
    if shw.match_os('Linux'): # Check the current platform
        # Java
        # ENV JAVA_HOME="/usr/lib/jvm/default-java"
        # ENV PATH="${PATH}:${JAVA_HOME}/bin/"
        shw.run('apt-get install -y  default-jre default-jdk lib32ncurses5 lib32z1')
        shw.run('')
        shw.run('')
        return False
    #---
    if enable:
        # Normal operation
        # /etc/default/grub
        # GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
        # Change to GRUB_CMDLINE_LINUX_DEFAULT="quiet splash libata.allow_tpm=1"
        # run update-grub
        # shw.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin yes')
        pass
    else:
        pass
        #shw.replace_line_in_file('/etc/ssh/sshd_config', 'PermitRootLogin', 'PermitRootLogin without-password')
    #---
    shw.run('service sshd restart')
    return batch.error_count
#---


def main():
    """ main function to parse arguments """
    exit_code = -1
    parser = argparse.ArgumentParser(description="Shell Receipes Engine", formatter_class=argparse.RawDescriptionHelpFormatter)
    # Global arguments
    parser.add_argument("--debug", action="store_true", default=False, help="Debug execution mode")
    parser.add_argument("--quiet", action="store_true", default=False, help="Quiet execution mode")

    subparsers = parser.add_subparsers(help='Supported commands', dest='command')

    configurables = ['rootssh','tcg']
    enable_parser = subparsers.add_parser('enable', help='Enable system configuration elements')
    enable_parser.add_argument('feature', action='store', help='Feature to enable', choices=configurables)
    disable_parser = subparsers.add_parser('disable', help='Disable system configuration elements')
    disable_parser.add_argument('feature', action='store', help='Feature to disable', choices=configurables)

    components = ['shrec', 'webmin','java']
    install_parser = subparsers.add_parser('install', help='Install components')
    install_parser.add_argument('--dir', action='store', default='', help='Installation directory')
    install_parser.add_argument('package', action='store', help='Package to install', choices=components)

    args = parser.parse_args()

    if args.command == 'install':
        batch = ShellWrapper(args.debug, args.quiet, "auto")
        if args.package == 'shrec':
            opt_path = '/opt'

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

            install_script(batch, 'bin2py.py', opt_path)
            install_script(batch, 'shrec.py',  opt_path)
            if batch.platform == 'Linux':
                batch.read_file('/etc/environment')
                idx = batch.search_forward(batch.text,'PATH')
                if idx<0:
                    pass # PATH is not found in /etc/environment
                else:
                    cur = batch.text[idx]
                    print(cur)
                #---
                batch.exit()
            else:
                # todo: windows
                pass
            #---
        #---
        batch.exit()
    #--

    if args.command == 'enable':
        batch = ShellWrapper(args.debug, args.quiet, "auto")
        if args.feature == 'rootssh':
            feature_rootssh(batch,True)
        elif args.feature == 'tcg':
            pass
        #---
    #---

    print("Unhandled command %s" % args.command)
    return -1
#---


if __name__ == "__main__":
    exit(main())
#---
