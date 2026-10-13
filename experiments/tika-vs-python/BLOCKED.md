# Tika vs Python extraction bake-off — blocked

Status: **preregistered, not executed**

The experiment in this directory remains valid and intentionally has **no empirical conclusion** yet.

## Environment observed

- Java 21 is available.
- Python 3.13 is available.
- Apache Tika is not preinstalled or present in local Maven/Gradle caches.
- JBang is not installed.
- The execution container cannot resolve outbound package/artifact hosts, and binary transfer of the pinned Tika artifact into the container was unavailable.

## Intended pinned arm

The preregistration uses Apache Tika **3.3.3** deliberately because the supported 3.x line still offers a single runnable `tika-app` JAR, isolating the extraction-coverage question from the additional distribution/plugin ceremony of Tika 4.x.

## Resume condition

Resume only when a verified Tika 3.3.3 application artifact is available locally or can be supplied to the experiment environment.

Do **not** treat this blocker as evidence for or against the Tika crossing-cost claim. The success criteria remain frozen in the preregistration.
