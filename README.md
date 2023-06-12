# Pull-Request-Generator

### Usage

```yaml
  - name: Pull-Request-Typography
    uses: chyccs/pull-request-typography@master
    continue-on-error: true
    with:
        language: python
        src_path: ${{ github.workspace }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

You can skip to set language variable if same as github detection

### 🪄 Bump dependabot🤖 pull request title

##### AS-IS
> build(deps): bump semgrep from 1.9.0 to 1.10.0

##### TO-BE
> build(deps): bump `semgrep` from `1.9.0` to `1.10.0`


### 🗂 Make your pull-request to `conventional pull-request`

##### AS-IS
> (Feat)Extends Singularize And Pluralize Symbols

##### TO-BE
> feat: extends `singularize` and `pluralize` symbols


### 🔦 Emphasize keywords

##### AS-IS
> Feat: Add make_test.py and resource files like en_us.res to achieve 100% testing

##### TO-BE
> feat: Add `make_test.py` and resource files like `en_us.res` to achieve `100%` testing

### Dependencies
* https://github.com/returntocorp/semgrep
# pull-request-generator
