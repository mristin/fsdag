"""Simply define DAG-workflows in Python where artefacts are stored on a filesystem."""

__version__ = "1.0.0"
__author__ = "Marko Ristin (marko@ristin.ch)"
__license__ = "MIT"
__status__ = "Production"

import abc
import logging
import pathlib
from typing import TypeVar, Generic, Optional

T = TypeVar("T")


class Node(Generic[T]):
    """Define a node in the workflow."""

    @abc.abstractmethod
    def _path(self) -> pathlib.Path:
        """Indicate path to the artefact."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _save(self, artefact: T) -> None:
        """Store the artefact on the filesystem to :py:meth:`_path`."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _load(self) -> T:
        """Load the artefact from the filesystem from :py:meth:`_path`."""
        raise NotImplementedError()

    @abc.abstractmethod
    def _compute(self) -> T:
        """Compute the artefact"""
        raise NotImplementedError()

    # NOTE (mristin):
    # We have to keep track of is-cached in a separate property in case that
    # the generic parameter T is set to None.
    _cached: bool
    _cached_artefact: Optional[T]

    logger: logging.Logger

    def __init__(self) -> None:
        self._cached = False
        self._cached_artefact = None

        self.logger = logging.getLogger(self.__class__.__qualname__)

    def done(self) -> bool:
        """Check whether the artefact has been already computed."""
        return self._path().exists()

    def resolve(self) -> T:
        """
        Resolve the node to the artefact.

        If the artefact is in the memory cache, return it immediately.

        If the artefact exists on the file system, load it, cache it, and return it.

        If the artefact is not available on the file system, compute it first, save
        it on the file system, cache it, and return it.
        """
        if self._cached:
            return self._cached_artefact  # type: ignore

        elif self.done():
            self._cached = True
            self.logger.info("Loading from: %s", self._path())
            self._cached_artefact = self._load()
            return self._cached_artefact

        else:
            self._cached = True
            self.logger.info("Computing...")
            self._cached_artefact = self._compute()
            self.logger.info("Saving to: %s", self._path())
            self._save(self._cached_artefact)

            return self._cached_artefact
