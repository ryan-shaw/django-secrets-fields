<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-review-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">DJANGO-SECRETS-FIELDS</h1></p>
<p align="center">
	<em><code>❯ Encrypted fields in Django</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/ryan-shaw/django-secrets-fields?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/ryan-shaw/django-secrets-fields?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/ryan-shaw/django-secrets-fields?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/ryan-shaw/django-secrets-fields?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

## 🔗 Table of Contents

- [📍 Overview](#-overview)
- [👾 Features](#-features)
- [📁 Project Structure](#-project-structure)
  - [📂 Project Index](#-project-index)
- [🚀 Getting Started](#-getting-started)
  - [☑️ Prerequisites](#-prerequisites)
  - [⚙️ Installation](#-installation)
  - [🤖 Usage](#🤖-usage)
  - [🧪 Testing](#🧪-testing)
- [📌 Project Roadmap](#-project-roadmap)
- [🔰 Contributing](#-contributing)
- [🎗 License](#-license)
- [🙌 Acknowledgments](#-acknowledgments)

---

## 📍 Overview

Django encrypted fields with support for multiple backends, currently supports symmetric encryption using Fernet and AWS Secrets Manager. Two fields types are currently supported, `SecretTextField` and `SecretJSONField`.

---

## 👾 Features

- **`Symmetric Encryption`**: Encrypt fields using Fernet encryption.
- **`AWS Secrets Manager`**: Use AWS Secrets Manager as a backend for storing secrets.
- **`Multiple Backends`**: Use multiple backends for different fields.

---
## 🚀 Getting Started

### ☑️ Prerequisites

Before getting started with django-secrets-fields, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python 3.10+


### ⚙️ Installation

Install django-secrets-fields:

```bash
pip install django-secrets-fields
```

To use backend that requires AWS install using:

```bash
pip install django-secrets-fields[aws]
```

### 🤖 Usage

**settings.py**
```python
DJANGO_SECRETS_FIELDS = {
    "default": {
        "backend": "secrets_fields.backends.encrypted.EncryptedBackend",
        "encryption_key": b"<fernet key>",
    },
    "aws": {
        "backend": "secrets_fields.backends.secretsmanager.SecretsManagerBackend",
        "prefix": "/path/",
    },
}
```

A [Fernet](https://cryptography.io/en/latest/fernet/) key can be generated using the following command:

```bash
python manage.py generate_fernet_key
```


**models.py**
```python
from django.db import models
from secrets_fields.fields import SecretJSONField, SecretTextField


class MyModel(models.Model):
	secret_text = SecretTextField(backend="aws")
	secret_json = SecretJSONField()

```

---
## 📌 Project Roadmap

- [X] **`Symmetric backend`**: <strike>Add symmetric encryption backend.</strike>
- [ ] **`Asymmetric backedn`**: Add asymmetric encryption backend.
- [ ] **`AWS Parameter Store`**: Add AWS Parameter Store backend.

---

## 🔰 Contributing

- **💬 [Join the Discussions](https://github.com/ryan-shaw/django-secrets-fields/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/ryan-shaw/django-secrets-fields/issues)**: Submit bugs found or log feature requests for the `django-secrets-fields` project.
- **💡 [Submit Pull Requests](https://github.com/ryan-shaw/django-secrets-fields/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/ryan-shaw/django-secrets-fields
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/ryan-shaw/django-secrets-fields/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=ryan-shaw/django-secrets-fields">
   </a>
</p>
</details>

---

## 🎗 License

This project is protected under the [MIT](https://choosealicense.com/licenses/mit) License. For more details, refer to the [LICENSE](https://github.com/ryan-shaw/django-secrets-fields/blob/main/LICENSE) file.

---
