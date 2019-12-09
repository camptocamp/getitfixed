Customization
=======================


Change Email content
--------------------

4 email templates exist

* admin_new_issue_email: received by the administrator of the category when a new issue is created

* new_issue_email: received by the reporter once the issue has been submitted

* update_issue_email: received by either reporter/administrator when an issue has been updated

* resolved_issue_email: received by the reporter once the issue has been resolved

These templates can be changed in the vars.yaml file


Change SMTP
-----------

In vars.yaml
change

.. code-block:: bash

       smtp:
        host: smtp


to the host of your smtp


Change Map aspect
-----------------

TODO (change background, ect)