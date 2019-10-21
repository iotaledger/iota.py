=====================
Contributing to PyOTA
=====================
So, you wanna contribute to PyOTA?  Awesome!  PyOTA is an important part of the IOTA ecosystem, and it's all thanks to people like you!

PyOTA is largely built and maintained by volunteers; by following a few "common sense" ground rules, we can make PyOTA stand out as a fun, exciting and rewarding project to work on.

Please take a few moments to read this guide to familiarize yourself with PyOTA's contributor code of conduct, and some of the ways you can contribute!

.. contents::
   :depth: 2


Ways You Can Help!
==================
There are lots of ways to get involved with PyOTA.  Many of them don't require writing any code (but if that's your thing, we've got you covered, too!).

- Improving Documentation
- Writing Tutorials
- Reporting Bugs
- Helping Users on the ``#python`` Channel on `Discord`_
- Fixing Bugs and Implementing New Features
- Writing Unit and Functional Tests

A Few Things that We Can't Accept
---------------------------------
We're pretty open about how people contribute to PyOTA, but there are a few things that we can't accept:

- Please do not post support requests here.  Use the ``#python`` channel on `Discord`_ 
- Please do not propose new API methods here.  There are multiple IOTA API libraries out there, and they must all have the same functionality.

  - That said, if you have an idea for a new API method, please share it on the ``#developers`` channel in `Discord`_ so that IOTA Foundation members can evaluate it!


Need Some Inspiration?
======================
If you would like to help out but don't know how to get started, here are some
places you can look for inspiration:

- Look for issues marked `help wanted`_ in the `PyOTA Bug Tracker`_
- Introduce yourself in the `#python` channel in `Discord`_ and watch for questions or issues that you can help with.
- Browse existing `tutorials`_ for other programming languages and create Python versions.

Is This Your First Contribution?
--------------------------------
Never contributed to an open-source project before?  No problem!  We're excited that you are considering PyOTA for your first contribution!

Please take a few minutes to read GitHub's guide on `How to Contribute to Open Source`_.  It's a quick read, and it's a great way to introduce yourself to how things work behind the scenes in open-source projects.


Guidelines for Reporting Bugs
=============================
Found a bug in the PyOTA code?  Great!  We can't fix bugs we don't know about; your bug report will go a long way toward helping PyOTA flourish.

Instructions
------------
1. Make sure it really is a PyOTA bug.

   - Check the traceback, and see if you can narrow down the cause of the bug.
   - If the error is not directly caused by PyOTA, or if you are unable to figure out what is causing the problem, we're still here for for you!  Post in the ``#python`` channel in `Discord`_ for assistance.

2. Is it safe to publish details about this bug publicly?

   - If the bug is security-related (e.g., could compromise a user's seed if exploited), or if it requires sensitive information in order to reproduce (e.g., the private key for an address), please do not post in in the PyOTA Bug Tracker!
   - To report security-related bugs, please contact ``@phx`` directly in `Discord`_.

3. Is this a known issue?

   - Before posting a bug report, check the `PyOTA Bug Tracker`_ to see if there is an existing issue for this bug.

4. Create a new issue in the `PyOTA Bug Tracker`_.

   - Be sure to include the following information:

     - Which version of PyOTA you are using.
     - Which version of Python you are using.
     - Which operating system you are using.
     - Instructions to reproduce the bug.
     - The expected behavior, if applicable.
     - The full exception traceback, if available.
       - If the exception also has a context object, please include it.

5. Please be nice!

   - It's frustrating when things don't work the way you expect them to.  We promise we didn't put that bug in there on purpose; we're all human, and we all make mistakes sometimes.

6. Please be patient!

   - We're committed to making to making PyOTA better, but we've also got jobs and other commitments.  We'll respond as soon as we can, but it might be a few days.

7. Please be responsive if follow-up is needed.

   - We may request additional information to help us identify/fix the bug.  The faster you respond to follow-up comments in your bug report, the sooner we can squash that bug!
   - If someone adds a comment to your bug report, it will appear in the `Notifications`_ page in GitHub.  You can also configure GitHub to `email you`_ when a new comment is posted.

What You Can Expect
-------------------
When you submit a bug report, here's what you can expect from the individual who reviews it:

- You can expect a response within one week of submission.
- If any additional information is needed, or if we are having trouble reproducing the issue you reported, you can expect a respectful and constructive response.


Guidelines for Developers
=========================
If you would like to contribute code to the PyOTA project, this section is for you!

Instructions
------------
1. Find an issue in the `PyOTA Bug Tracker`_ to work on.

   - If you want to work on a bug or feature that doesn't have a GitHub issue yet, create a new one before starting to work on it.  That will give other developers an opportunity to provide feedback and/or suggest changes that will make it integrate better with the rest of the code.

2. Create a fork of the PyOTA repository.
3. Create a new branch just for the bug/feature you are working on.

   - If you want to work on multiple bugs/features, you can use branches to keep them separate, so that you can submit a separate Pull Request for each one.

4. Once you have completed your work, create a Pull Request, ensuring that it meets the requirements listed below.

Requirements for Pull Requests
------------------------------
PyOTA is a critical component for many applications, and as such its code must be of exceptionally high quality.  To help maintain reliability and code quality, there are a few requirements for contributions.

This is a big list, but don't let it intimidate you!  Many of these are "common sense" things that you probably do already, but we have to list them here anyway, just so that there's no confusion.

If you have any questions, please feel free to post in the ``#python`` channel in `Discord`_!

- Please create Pull Requests against the ``develop`` branch.
- Please limit each Pull Request to a single bugfix/enhancement.
- Please limit the scope of each Pull Request to just the changes needed for that bugfix/enhancement.

  - If you would like to refactor existing code, please create separate Pull Request(s) just for the refactoring.

- Please ensure your code works in all supported versions of Python (this includes versions of Python 2 and Python 3).

  - See ``README.rst`` for the list of supported Python versions.

- Please ensure that your Pull Request includes full test coverage.
- Please do not introduce new dependencies unless absolutely necessary.
- When introducing new classes/functions, please write comprehensive and meaningful docstrings.  It should be clear to anyone reading your code what your new class/function does and why it exists.
  - Similarly, please be liberal about adding comments to your code.  If you have any knowledge and/or had to do any research that would make your code easier to understand, add it as comment.  Future developers will be very grateful for the extra context!

  - Please ensure that your comments and docstrings use proper English grammar and spelling.

- Please ensure that your code conforms to `PEP-8`_.

  - Much of the existing code is not currently formatted for PEP-8; where practical, you may prefer PEP-8 over being consistent with the existing code.
  - We are currently converting the codebase over to PEP-8; `come on over and help us out!`_

What You Can Expect
-------------------
When you submit a Pull Request, here is what you can expect from the individual who reviews it:

- You can expect a response within one week of submission.
- If any changes are needed, or if we cannot accept your submission, we will provide a respectful and constructive explanation.


.. _come on over and help us out!: https://github.com/iotaledger/iota.py/issues/145
.. _email you: https://help.github.com/articles/managing-notification-delivery-methods/
.. _help wanted: https://github.com/iotaledger/iota.py/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22
.. _how to contribute to open source: https://opensource.guide/how-to-contribute/
.. _notifications: https://github.com/notifications
.. _pep-8: https://www.python.org/dev/peps/pep-0008/
.. _pyota bug tracker: https://github.com/iotaledger/iota.py/issues
.. _discord: https://discord.iota.org
.. _tutorials: https://docs.iota.org
