# Correctness

Fires: always

Leading word: **the edge**. Most shipped bugs are not exotic: an off-by-one, an inverted condition, a float compared with `==`, a result computed and thrown away, a file left open on the error path. Read each critical function as a hostile reviewer who runs it on the first, the last, the empty and the huge input.

Artifact: an edge table (function on a critical path → its edges: empty, one, max, negative, missing, non-ASCII → what it returns for each).

- **boundaries**: Ranges and indexes at their ends: `<` versus `<=`, inclusive versus exclusive ends, `length - 1`, the first and last page, an empty collection, a single element, the exact limit (quota 5 of 5, a 10 MB file at 10 MB). Write the call at each edge and read what comes back.
- **null-paths**: Every value that can be `null`, `nil`, `None` or `undefined` on some path: a lookup that finds nothing, an optional field the server omits, a force unwrap, `!`, `.get()` with no default, optional chaining that turns "missing" into a silent `undefined` the next line treats as real.
- **numeric**: Integer overflow and truncation, integer division where a fraction was meant, floats compared with `==`, `NaN` and `Infinity` flowing into storage, `parseInt` without a radix, rounding that runs before the last step, a percentage over 100, a negative where the domain has none. Money arithmetic belongs to the money lens.
- **equality-identity**: Reference equality where value equality was meant (`===` on objects, `is` on strings and numbers in Python, `==` on Java strings), mutable default arguments, a shared object mutated by one caller and seen by another, a list copied shallowly then changed, hash keys that change after insertion.
- **inverted-logic**: Negations and combinations that say the opposite of the intent: `!a || !b` where `!(a && b)` was not meant, `&&` and `||` swapped, operator precedence (`a & b == c`, `!x in y`), an early return that skips cleanup or the audit log, a guard that checks the wrong variable.
- **resource-leak**: Files, sockets, database connections, cursors, locks and transactions opened on a path that can throw or return early before they close. Look for `open` with no `with`/`using`/`defer`/`try-with-resources`/`finally`, pools that run dry under errors, and locks never released on the error branch.
- **text-encoding**: Byte length used as character length, string slicing that splits an emoji or a surrogate pair, Unicode normalization (é as one or two code points) in comparisons and unique keys, case-insensitive comparison by `toLowerCase` (Turkish İ), a default encoding that differs between machines, line endings, a BOM.
- **regex**: Patterns missing `^`/`$` anchors used as validators, `.` matching more than meant, unescaped input built into a pattern, and nested quantifiers like `(a+)+` run on user input, which backtrack for minutes (ReDoS).
- **copy-paste**: Near-duplicate blocks where one copy was not updated: the same variable twice in a comparison (`a.x == a.x`), the last line of a repeated block still naming the previous field, a branch body identical to its sibling. Duplicated logic as a design problem belongs to the design lens; this probe looks for the copy that is already wrong.
- **ignored-result**: A computed value that is thrown away: an unawaited promise or coroutine, `str.replace` or `sorted` whose result is unused, a returned error that is never checked (`_ = f()`, Go's unchecked `err`), a `map` called for side effects, a `filter` whose result is dropped.

Confirm with a failing test at the nearest seam: each edge is one assertion.

Done: every function on a critical path has a row in the edge table with an answer for each edge, and every resource opened on a critical path has a close on every exit.
