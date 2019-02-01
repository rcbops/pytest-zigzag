Config Property Overrides
=========================

In order to provide a convenient way to configure pytest zigzag on the fly,
users are allowed to override any config property defined in the pytest
config file with an environment variable.


Given the following config:

```javascript
{
  "pytest_zigzag_env_vars": {
    "BUILD_URL": null,
    "BUILD_NUMBER": null
  }
}
```

one could override the BUILD_URL parameter by executing the following on
the command line before running pytest:

```bash
export BUILD_URL="new value"

```
