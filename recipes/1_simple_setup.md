In this document we'll walk through 2 examples, one is the php default build, which can be sufficient for some, but it's advisable to compile only what you need. I find it benefitial in multiple fronts.

so, let's start with the default

elbuilder install 8.4.8

elbuilder use 8.4.8


### Dual versions

elbuilder install 8.3.22

elbuilder use 8.3.22

switching is as easy as you see using the use command

### Persisting a certain version to be the default

```
echo 'eval "$(elbuilder use 8.3.22)"' >> ~/.zshrc

or

echo 'eval "$(elbuilder use 8.3.22)"' >> ~/.bashrc
```
