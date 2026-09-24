# Public Boundary archive publication still needed

The two candidate commits exist in Git history, but they are not currently usable P10 publication evidence.

Anonymous GitHub access to the configured repository/archive returned HTTP 404:

    https://github.com/dmos62/speckit-specdd
    https://github.com/dmos62/speckit-specdd/archive/b43741a19ce12cc408fd493c25df17541e5a46c9.tar.gz

P10 requires anonymously retrievable immutable commit archives. A commit reachable through an authenticated Git remote is not sufficient.

Please publish both required commits through a public GitHub repository according to the repository's normal policy. The intended revisions remain:

    ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e
    b43741a19ce12cc408fd493c25df17541e5a46c9

If `https://github.com/dmos62/speckit-specdd` is intended to be the public source, make that repository anonymously readable and confirm both commits remain reachable there.

Then verify from an unauthenticated shell:

    set -euo pipefail
    repo=https://github.com/dmos62/speckit-specdd

    curl -fL "$repo" -o /dev/null

    for commit in \
      ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e \
      b43741a19ce12cc408fd493c25df17541e5a46c9
    do
      archive=$(mktemp)
      curl -fL --retry 3 \
        "$repo/archive/$commit.tar.gz" \
        -o "$archive"
      printf '%s  %s\n' \
        "$(sha256sum "$archive" | awk '{print $1}')" \
        "$commit"
      rm -f "$archive"
    done

Return the two printed SHA-256 values after the anonymous downloads succeed.

If the repository must remain private, publish these genuine implementation revisions to another public GitHub repository and return that repository URL instead. Do not use authenticated-only downloads, mutable branch/tag archives, synthetic archive bytes, or fabricated checksums.

Once anonymous publication succeeds, the next iteration can create the release fixtures, run the release-proof matrix, and delete this file.

------------

Response:

````
domas@h87m-g43-win10:~/projects/speckit-specdd$     set -euo pipefail
    repo=https://github.com/dmos62/speckit-specdd

    curl -fL "$repo" -o /dev/null

    for commit in \
      ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e \
      b43741a19ce12cc408fd493c25df17541e5a46c9
    do
      archive=$(mktemp)
      curl -fL --retry 3 \
        "$repo/archive/$commit.tar.gz" \
        -o "$archive"
      printf '%s  %s\n' \
        "$(sha256sum "$archive" | awk '{print $1}')" \
        "$commit"
      rm -f "$archive"
    done
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
100 321.7k   0 321.7k   0      0 464.6k      0                              0
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0
100 246.9k   0 246.9k   0      0 244.9k      0           00:01              0
2dd4b6231e63d1c236c5d715b6852aad4ca28a77208c9248c6614ef79a0600d5  ab7302e1d6986e0ce0db9ac8a567999e6aa3a50e
  % Total    % Received % Xferd  Average Speed  Time    Time    Time   Current
                                 Dload  Upload  Total   Spent   Left   Speed
  0      0   0      0   0      0      0      0                              0
100 242.3k   0 242.3k   0      0 223.0k      0           00:01              0
158db005bad253bd57b56cb9ea4697cbac4d29ad886248bf2ee0c05827774353  b43741a19ce12cc408fd493c25df17541e5a46c9
````
