Downstream consumer ran into problems, see BOUNDARY-FEEDBACK.md. Note, look at revision ids: first report is about an earlier revision (outdated).

The current iteration still did not receive the contents of BOUNDARY-FEEDBACK.md, so no runtime fix can be derived safely. Compare the feedback against the current revision before changing consumer behavior.

Harness regressions found in this iteration were corrected for the next iteration:

- consumer-focused tests now run through Python's built-in unittest runner instead of requiring an unavailable pytest executable;
- the file-size check no longer depends on shell-sensitive awk positional variables;
- files.include is narrowed to downstream consumer, installation, and directly relevant lifecycle tests while retaining the required BOUNDARY-FEEDBACK.md inclusion.
