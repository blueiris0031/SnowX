from sys import argv as sys_argv


if __name__ == "__main__":
    if len(sys_argv) > 1:
        from tools.tools_runner import main
    else:
        from framework.main import main

    main()
