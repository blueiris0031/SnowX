if __name__ == '__main__':
    from framework.kernel import main

    main()
else:
    from warnings import warn

    warn("Import mode is no longer available.", RuntimeWarning)


__all__ = []
