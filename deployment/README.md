TEStribute K8S deploy generator
===============================

The script (`deploy.sh`)  is self-documenting:

```bash
$ ./deploy.sh -h
TEStribute deployer.

Usage:
	<envVar1>=<value1> <envVar2>=<value2> ... ./deploy.sh -d | kubectl -n <namespace> create -f -

Env vars:
	TESTRIBUTE_IMAGE: Use this image URI to run TEStribute.
	Default: elixircloud/testribute:latest

	TESTRIBUTE_HOST: Expose TEStribute at this host.
	Default: testribute
```


