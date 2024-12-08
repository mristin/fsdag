# fsdag



This library allows you to simply define DAG-workflows in Python where artefacts are stored on a filesystem.

Fsdag aims at simple personal or group projects, where no dependencies and simplicity are paramount.
It is implemented in less than 100 lines of code.

For more complex workflow libraries, see:
* [pydags],
* [hamilton],
* [luigi],
* ... and many others on: https://github.com/pditommaso/awesome-pipeline

[pydags]: https://pypi.org/project/pydags/
[hamilton]: https://pypi.org/project/sf-hamilton/
[luigi]: https://pypi.org/project/luigi/

## Approach

You simply define nodes of your workflow, and execute them lazily.
Each node corresponds to an artefact.
If the artefact already exists on the filesystem, it will be loaded; otherwise, it will be computed.
Once loaded or computed, the artefacts are kept in memory for further access.

## Installation

To install fsdag, simply run the following command in your virtual environment:
```
pip3 install fsdag
```

## Usage

The workflow node is implemented as an abstract class `fsdag.Node`.
For your concrete nodes, you have to implement the following methods:
* `_path`: where the artefact should be stored on disk,
* `_save`: how to store the artefact to `_path()`,
* `_load`: how to load the artefact from `_path()`, and
* `_compute`: how to compute the artefact.

To resolve the node, call `resolve()`.

## Examples

### Basic Example

Here is an example showing how you can model a node where the data is de/serialized using JSON.

```python
import json
import pathlib
from typing import List

import fsdag

class Something(fsdag.Node[List[int]]):
    def _path(self) -> pathlib.Path:
        return pathlib.Path("/some/path/something.json")

    def _save(self, artefact: List[int]) -> None:
        self._path().write_text(json.dumps(artefact))

    def _load(self) -> List[int]:
        return json.loads(
            self._path().read_text()
        )  # type: ignore

    def _compute(self) -> List[int]:
        return [1, 2, 3]

something = Something()
print(something.resolve())
# Outputs: [1, 2, 3]
# The artefact is now saved to the filesystem. It is also kept
# in memory # for faster access if you ever resolve it again.

# For example, calling ``resolve`` here again retrieves
# the artefact from the memory cache:
print(something.resolve())
# Outputs: [1, 2, 3]

another_something = Something()
# This call to the ``resolve`` method will not perform
# the computation, but load the artefact from the filesystem.
print(another_something.resolve())
# Outputs: [1, 2, 3]
```

### `None` Artefact

Some tasks contain no artefact, *i.e.*, they are mere procedures which should be executed, but return nothing.
To model such procedures, use `None` as the generic parameter and a marker file:

```python
import pathlib

import fsdag

class Something(fsdag.Node[None]):
    def _path(self) -> pathlib.Path:
        return pathlib.Path("/path/to/somewhere/done")

    def _save(self, artefact: None) -> None:
        self._path().write_text("done")

    def _load(self) -> None:
        return

    def _compute(self) -> None:
        # Perform some complex procedure.
        ...
        return

something = Something()
# The procedure is executed here once.
something.resolve()

another_something = Something()
# This resolution does nothing as the procedure 
# has been already executed.
another_something.resolve()
```

### Workflow Graph

Here is a full example of a simple workflow graph.

```python
import json
import pathlib

import fsdag

class Something(fsdag.Node[int]):
    def _path(self) -> pathlib.Path:
        return pathlib.Path("/some/path/something.json")

    def _save(self, artefact: int) -> None:
        self._path().write_text(json.dumps(artefact))

    def _load(self) -> int:
        return json.loads(
            self._path().read_text()
        )  # type: ignore

    def _compute(self) -> int:
        return 1


class Another(fsdag.Node[int]):
    def _path(self) -> pathlib.Path:
        return pathlib.Path("/some/path/another.json")

    def _save(self, artefact: int) -> None:
        self._path().write_text(json.dumps(artefact))

    def _load(self) -> int:
        return json.loads(
            self._path().read_text()
        )  # type: ignore

    def _compute(self) -> int:
        return 2

class Sum(fsdag.Node[int]):
    def __init__(
            self, 
            something: Something, 
            another: Another
    ) -> None:
        super().__init__()
        self.something = something
        self.another = another
    
    def _path(self) -> pathlib.Path:
        return pathlib.Path("/some/path/sum.json")

    def _save(self, artefact: int) -> None:
        self._path().write_text(json.dumps(artefact))

    def _load(self) -> int:
        return json.loads(
            self._path().read_text()
        )  # type: ignore

    def _compute(self) -> int:
        # Note the calls to ``resolve`` methods here.
        return (
            self.something.resolve() 
            + self.another.resolve()
        )

something = Something()
another = Another()

result = Sum(something=something, another=another)

# The call to ``result.resolve`` will recursively and 
# lazily resolve the ``something`` and ``another``.
print(result.resolve())
# Outputs: 3
```