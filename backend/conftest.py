def pytest_addoption(parser):
    parser.addoption(
        "--backend",
        action="store",
        default="local",
        choices=("local", "docker"),
        help="Run tests against local backend or docker backend",
    )