"""Focused no-network checks of ASR hygiene and rendered evidence identities."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    sound = load('sound_checks', 'prepare-sound.py')
    renderer = load('render_checks', 'render-pilot.py')
    cases = [('Real spoken words.', False, 'Real spoken words.'),
        ('you', True, None), ('*Crowing*', False, None), ('♪', False, None),
        ('<unk>' * 20, False, None), ('Nine <unk>', False, None), ('', False, None),
        ('Thank you.', False, 'Thank you.')]
    for raw, zero, expected in cases:
        assert sound.guarded_speech(raw, zero) == expected
    # The final guard still produces the same frozen context for all actual Whisper cells.
    guards = json.loads((HERE / 'asr-guards.json').read_text())
    for row in guards.values():
        assert sound.guarded_speech(row['raw_asr_text'], row['digital_zero']) == row['candidate_speech_text']
    renderer.offline_check()
    (HERE / 'offline-validation.json').write_text(json.dumps({
        'network_calls': 0, 'asr_guard_cases_passed': len(cases),
        'frozen_asr_context_unchanged': True,
        'renderer_checks': 'one valid case and six adversarial cases passed',
        'limits': 'A plausible lexical transcript on nonzero audio remains an unverified candidate; these guards cannot establish acoustic truth.'}, indent=2) + '\n')
    print('Eight ASR guard cases, frozen context equality, and renderer adversarial checks passed. No inference.')


if __name__ == '__main__':
    main()
