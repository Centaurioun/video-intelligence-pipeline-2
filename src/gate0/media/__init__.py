"""Measured local-media adapters for Gate-0.

Modules:

``gate0.media.proc``
    The single bounded, fail-closed subprocess seam for local media tools.
``gate0.media.tool_identity``
    Deterministic, digest-bound identity of a local media tool build.
``gate0.media.probe``
    Real ``ffprobe`` probe adapter producing measured ``ProbeEvidence``.
``gate0.media.decode``
    Real ``ffprobe``/``ffmpeg`` decode adapter producing ``DecodedFrame``
    sequences with measured presentation PTS.
"""
