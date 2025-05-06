from pathlib import Path

import pytest


def test_substitution(config_dir: Path):
    from tarmac.runner import Runner

    runner = Runner(base_path=str(config_dir))
    (config_dir / "workflows").mkdir()

    def check(subst: str, expected):
        with open(config_dir / "workflows" / "substitution.yml", "w") as f:
            f.write(
                f"""
steps:
  - id: test
    py: |
      for inp in inputs['tests']:
        outputs[inp] = inputs['tests'][inp]
    with:
      tests:
        test: {subst}
"""
            )
        outputs = runner.execute_workflow("substitution", {})
        assert outputs["steps"]["test"]["test"] == expected

    check(".$", ".$")
    check(".$$", ".$$")
    check(".${", ".${")
    check(".$${", ".$${")
    check(".${{", ".${{")
    check(".$${{", ".$${{")
    check(".$$${{", ".$$${{")
    check(".${a", ".${a")
    check(".$${a", ".$${a")
    check(".$$${a", ".$$${a")
    check(".${123}", ".123")
    check(".$${123}", ".${123}")
    check(".$$${123}", ".$123")
    check(".$$$${123}", ".$${123}")
    check(".$$$$${123}", ".$$123")
    check(".${123.456}", ".123.456")
    with pytest.raises(SyntaxError):
        check(".${123.456.789}", "")
    with pytest.raises(NameError):
        check(".${alice}", "")
    with pytest.raises(KeyError):
        check(".${dict(alice='bob')['bob']}", "")
    check(".${dict(alice='bob')['alice']}", ".bob")
    check(".${dict(alice='bob')['alice']", ".${dict(alice='bob')['alice']")
    check(".${'$'}", ".$")
    check(".$$$$$$${'\\x7b'}", ".$$${")
    check(".${123}}", ".123}")
    check(".${123}}}", ".123}}")
    check(".${123}}}}", ".123}}}")
    check(
        """
        - ${"Hello"}
        - world:
            - ${"nested"}
            - ${"substitution"}
            - ${"test"}
        """,
        ["Hello", {"world": ["nested", "substitution", "test"]}],
    )
    import sys

    check("${__import__('sys').platform}", sys.platform)

    check("123", 123)
    check("123.456", 123.456)
