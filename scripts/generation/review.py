"""Hash-bound human review receipts. A recorded approval is not independent ground truth."""
import hashlib

CHECKS = ('audible_events', 'timing', 'wording', 'simultaneous_events', 'reading_time')


def cue_digest(cue):
    import json
    return hashlib.sha256(json.dumps(cue, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def review_receipt(track, caption_hash, video_hash, selected):
    return {
        'version': 1, 'caption_sha256': caption_hash, 'video_sha256': video_hash,
        'reviewer_id': '', 'scope': 'Human listening/wording review, not participant evaluation or a model score.',
        'cues': [{'cue_id': cue['cue_id'], 'cue_sha256': cue_digest(cue),
                  'checks': {name: 'pending' for name in CHECKS},
                  'variants': {name: 'pending' for name in cue['grid']}, 'note': ''} for cue in selected],
        'total_track_cues': len(track['cues']),
    }


def validate_review(track, caption_hash, video_hash, receipt):
    if receipt.get('caption_sha256') != caption_hash or receipt.get('video_sha256') != video_hash:
        raise ValueError('Review hashes do not match the current captions and exact video.')
    reviewer = receipt.get('reviewer_id')
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError('A human reviewer ID is required; do not invent an approval.')
    indexed = {cue['cue_id']: cue for cue in track['cues']}
    seen = set()
    for item in receipt.get('cues', []):
        identity = item.get('cue_id')
        if identity not in indexed or identity in seen:
            raise ValueError('Unknown or duplicate cue in review receipt.')
        seen.add(identity); cue = indexed[identity]
        if item.get('cue_sha256') != cue_digest(cue):
            raise ValueError('Reviewed cue changed; repeat its listening and wording review.')
        checks, variants = item.get('checks', {}), item.get('variants', {})
        if set(checks) != set(CHECKS) or set(variants) != set(cue['grid']):
            raise ValueError('Every review dimension and all nine variants need explicit decisions.')
        if any(value != 'approved' for value in [*checks.values(), *variants.values()]):
            raise ValueError('Pending or rejected review decisions remain; no track accepted.')
    if seen != set(indexed):
        raise ValueError('Only a subset was reviewed; whole-track review is incomplete.')
    return {'status': 'documented-human-review-complete', 'cue_count': len(seen),
            'notice': 'Self-reported review completion only. No automatic installation, independent review, DHH validation or accessibility benefit is established.'}
