# Tutorial: Installing Multiple versions

In this tutorial we are going to install PHP 8.3.22 and 8.4.8 running simultaneously with shell integration.

## 1. Check Dependencies

```bash
elbuilder doctor
```

Install deps based on output:

**Linux (Ubuntu/Debian):**
```bash
sudo apt install bison autoconf re2c build-essential libxml2-dev libcurl4-openssl-dev
```

**Linux (RHEL/CentOS/AlmaLinux):**
```bash
sudo yum install bison autoconf re2c gcc gcc-c++ libxml2-devel libcurl-devel
```

**macOS:**
```bash
brew install bison autoconf re2c
```

Run `elbuilder doctor` - should show all OK.

## 2. Install PHP Versions

```bash

elbuilder install 8.3.22

  
elbuilder install 8.4.8
```



## 3. Setup Shell Integration

```bash
elbuilder setup
```

Restart terminal or:
```bash
source ~/.bashrc  # or ~/.zshrc
```

## 4. Switch Between Versions

```bash
# Use 8.3.22
elbuilder use 8.3.22
php -v

# switch to 8.4.8
elbuilder use 8.4.8
php -v

# Check installed versions
elbuilder installed
```

## 5. Verify Setup

```bash
which php        # Should point to ~/.elbuilder/shims/php
php -v
```

Done. Both versions installed, shims active, switch anytime with `elbuilder use X.Y.Z`.

