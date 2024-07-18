"""This module contains utility functions for the project.

Attributes:
    * __all__: List of all modules in the package.

Modules:
    * mail: Functions for handling email addresses.

Functions:
    * split_email: Splitting an email address into username and domain.
"""
from .mail import split_email

__all__ = [split_email]
