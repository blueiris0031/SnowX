from sys import argv as sys_argv


if __name__ == '__main__':
    from framework.main.d_start_mode import main
    main(*sys_argv[1:])
else:
    from framework.main.import_mode import main
    print(f"Import mode return code: {main(*sys_argv[1:])}")
