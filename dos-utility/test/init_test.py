from dos_utility import main


def test_main(capsys):
    """Test that main() prints the expected greeting."""
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from dos-utility!\n"
