# Changelog

## [«unknown»](https://github.com/NASA-PDS/deep-archive/tree/«unknown») (2025-07-02)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.3.0...«unknown»)

**Requirements:**

- As a user, I want deep archive to support LBLX label extensions [\#157](https://github.com/NASA-PDS/deep-archive/issues/157)

**Defects:**

- Output manifest .tab files do not use forward slashes on Windows [\#208](https://github.com/NASA-PDS/deep-archive/issues/208) [[s.medium](https://github.com/NASA-PDS/deep-archive/labels/s.medium)]
- pds-deep-registry-archive produces incomplete SIPs for data recently uploaded to the Registry [\#202](https://github.com/NASA-PDS/deep-archive/issues/202) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]

## [v1.3.0](https://github.com/NASA-PDS/deep-archive/tree/v1.3.0) (2024-10-16)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.2.0...v1.3.0)

**Defects:**

- AIP now fails validation after \#178 update [\#186](https://github.com/NASA-PDS/deep-archive/issues/186) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]
- Issues with manifests after multiple slash update fix \(\#162\) [\#178](https://github.com/NASA-PDS/deep-archive/issues/178) [[s.medium](https://github.com/NASA-PDS/deep-archive/labels/s.medium)]
- Failing build due to deprecated config [\#171](https://github.com/NASA-PDS/deep-archive/issues/171) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]

**Other closed issues:**

- Remove all versions support from deep-archive until the API provides support for this [\#179](https://github.com/NASA-PDS/deep-archive/issues/179)
- Update tests to use more stable test data on pds.nasa.gov versus an external site [\#169](https://github.com/NASA-PDS/deep-archive/issues/169)

## [v1.2.0](https://github.com/NASA-PDS/deep-archive/tree/v1.2.0) (2024-05-28)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.1.5...v1.2.0)

**Requirements:**

- As a data custodian, I want the Deep Archive to work around invalid URLs in the Registry [\#162](https://github.com/NASA-PDS/deep-archive/issues/162)

## [v1.1.5](https://github.com/NASA-PDS/deep-archive/tree/v1.1.5) (2024-02-27)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.1.4...v1.1.5)

**Improvements:**

- Upgrade deep-archive to comply with latest search API changes \(API v1.4.0 / pds-api-client v1.5.0\) [\#159](https://github.com/NASA-PDS/deep-archive/issues/159)

**Defects:**

- Transfer manifest mismatch between `pds-deep-archive` and `pds-deep-registry-archive` [\#158](https://github.com/NASA-PDS/deep-archive/issues/158) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]
- pds-deep-registry-archive produces invalid SIPs/AIPs [\#155](https://github.com/NASA-PDS/deep-archive/issues/155) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]

## [v1.1.4](https://github.com/NASA-PDS/deep-archive/tree/v1.1.4) (2024-01-08)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.1.3...v1.1.4)

**Defects:**

- Installation instructions don't work on Windows 11 [\#151](https://github.com/NASA-PDS/deep-archive/issues/151) [[s.medium](https://github.com/NASA-PDS/deep-archive/labels/s.medium)]
- Install issue with Python 3.11 [\#149](https://github.com/NASA-PDS/deep-archive/issues/149) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]
- Jenkins Deep Regsitry Archive ran for the first time, failed [\#147](https://github.com/NASA-PDS/deep-archive/issues/147)

## [v1.1.3](https://github.com/NASA-PDS/deep-archive/tree/v1.1.3) (2023-04-11)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.1.2...v1.1.3)

**Defects:**

- Canonical path is not processed correctly \('/../ in path\) [\#145](https://github.com/NASA-PDS/deep-archive/issues/145) [[s.critical](https://github.com/NASA-PDS/deep-archive/labels/s.critical)]
- Pagination handling does not appear to work properly for pds-deep-registry-archive [\#137](https://github.com/NASA-PDS/deep-archive/issues/137) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]
- Cannot connect to any PDS API endpoints for pds-deep-archive-registry [\#134](https://github.com/NASA-PDS/deep-archive/issues/134) [[s.high](https://github.com/NASA-PDS/deep-archive/labels/s.high)]

**Other closed issues:**

- integrate deep archive to staging tests [\#138](https://github.com/NASA-PDS/deep-archive/issues/138)
- Change default API endpoint to the operational API on pds.nasa.gov [\#133](https://github.com/NASA-PDS/deep-archive/issues/133)
- README.md link errors [\#131](https://github.com/NASA-PDS/deep-archive/issues/131)

## [v1.1.2](https://github.com/NASA-PDS/deep-archive/tree/v1.1.2) (2022-05-17)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.1.1...v1.1.2)

**Other closed issues:**

- Upgrade to latest PDS API Client [\#128](https://github.com/NASA-PDS/deep-archive/issues/128)

## [v1.1.1](https://github.com/NASA-PDS/deep-archive/tree/v1.1.1) (2022-04-14)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.1.0...v1.1.1)

**Improvements:**

- Update PDS Deep "Registry" Archive and remove workaround + implement latest-only-feature per API updates [\#107](https://github.com/NASA-PDS/deep-archive/issues/107)

**Defects:**

- Unexpected fatal error when running pds-deep-archive against bundle [\#124](https://github.com/NASA-PDS/deep-archive/issues/124) [[s.medium](https://github.com/NASA-PDS/deep-archive/labels/s.medium)]

## [v1.1.0](https://github.com/NASA-PDS/deep-archive/tree/v1.1.0) (2021-09-29)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v1.0.0...v1.1.0)

**Improvements:**

- Improvements per API updates to remove workarounds from code [\#106](https://github.com/NASA-PDS/deep-archive/issues/106)
- NSSDCA Delivery Onboarding [\#80](https://github.com/NASA-PDS/deep-archive/issues/80)

**Defects:**

- deep archive misses products that specify primary products using lower case 'p' [\#116](https://github.com/NASA-PDS/deep-archive/issues/116) [[s.low](https://github.com/NASA-PDS/deep-archive/labels/s.low)]

**Other closed issues:**

- Retrofit pds-deep-archive to use pds python template [\#111](https://github.com/NASA-PDS/deep-archive/issues/111)

## [v1.0.0](https://github.com/NASA-PDS/deep-archive/tree/v1.0.0) (2021-05-03)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.5.0...v1.0.0)

## [v0.5.0](https://github.com/NASA-PDS/deep-archive/tree/v0.5.0) (2021-05-03)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.4.0...v0.5.0)

**Requirements:**

- As a user, I want the SIP manifest to include valid URLs [\#102](https://github.com/NASA-PDS/deep-archive/issues/102)
- As a user, I want to generate AIPs and SIPs using Registry [\#7](https://github.com/NASA-PDS/deep-archive/issues/7)

**Defects:**

- aip\_label\_checksum is not for the correct file [\#99](https://github.com/NASA-PDS/deep-archive/issues/99)

## [v0.4.0](https://github.com/NASA-PDS/deep-archive/tree/v0.4.0) (2021-01-25)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.3.2...v0.4.0)

**Improvements:**

- Bash required for default installation description [\#95](https://github.com/NASA-PDS/deep-archive/issues/95)
- add year to directory path in URL [\#93](https://github.com/NASA-PDS/deep-archive/issues/93)

## [v0.3.2](https://github.com/NASA-PDS/deep-archive/tree/v0.3.2) (2021-01-12)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.3.1...v0.3.2)

**Defects:**

- SIP manifest table erroneously includes secondary collections and their basic products [\#92](https://github.com/NASA-PDS/deep-archive/issues/92)
- Small typo on package documentation [\#90](https://github.com/NASA-PDS/deep-archive/issues/90)

## [v0.3.1](https://github.com/NASA-PDS/deep-archive/tree/v0.3.1) (2020-11-30)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.2.3...v0.3.1)

## [v0.2.3](https://github.com/NASA-PDS/deep-archive/tree/v0.2.3) (2020-11-30)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.2.2...v0.2.3)

**Other closed issues:**

- Test on Windows [\#76](https://github.com/NASA-PDS/deep-archive/issues/76)

## [v0.2.2](https://github.com/NASA-PDS/deep-archive/tree/v0.2.2) (2020-10-22)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.2.1...v0.2.2)

**Improvements:**

- Update Github Actions for dev and ops releases [\#81](https://github.com/NASA-PDS/deep-archive/issues/81)

**Defects:**

- Output SIP manifest has invalid URLs [\#85](https://github.com/NASA-PDS/deep-archive/issues/85)

## [0.2.1](https://github.com/NASA-PDS/deep-archive/tree/0.2.1) (2020-10-09)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.2.0...0.2.1)

**Defects:**

- Output SIP uses backslash in output URLs on Windows [\#82](https://github.com/NASA-PDS/deep-archive/issues/82)
- Standalone AIP Generator Fails [\#78](https://github.com/NASA-PDS/deep-archive/issues/78)

## [0.2.0](https://github.com/NASA-PDS/deep-archive/tree/0.2.0) (2020-10-02)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.1.6...0.2.0)

**Improvements:**

- Organize the automated documentation generation for dev releases [\#74](https://github.com/NASA-PDS/deep-archive/issues/74)
- Minor software Improvements from Initial release [\#30](https://github.com/NASA-PDS/deep-archive/issues/30)

**Defects:**

- Deep Archive doesn't do Windows [\#77](https://github.com/NASA-PDS/deep-archive/issues/77)
- Update CI/CD to fix PyPi deployment failure and improve documentation deployment [\#58](https://github.com/NASA-PDS/deep-archive/issues/58)

**Other closed issues:**

- Notify nodes of operational release of PDS Deep Archive [\#67](https://github.com/NASA-PDS/deep-archive/issues/67)
- Begin initial deliveries of data to NSSDCA with Phase 1 nodes [\#66](https://github.com/NASA-PDS/deep-archive/issues/66)

## [0.1.6](https://github.com/NASA-PDS/deep-archive/tree/0.1.6) (2020-07-15)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.1.5...0.1.6)

**Defects:**

- Invalid filenames to match SIP / AIP LIDs [\#75](https://github.com/NASA-PDS/deep-archive/issues/75)

## [0.1.5](https://github.com/NASA-PDS/deep-archive/tree/0.1.5) (2020-07-02)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.1.4...0.1.5)

**Requirements:**

- The Submission Information Package manifest shall be a tab-delimited table with one record per product and four fields per record containing the following fields: checksum value, checksum type, resolvable URL to data product, unique product lidvid for the associated product [\#54](https://github.com/NASA-PDS/deep-archive/issues/54)

**Other closed issues:**

- Test Case 5: Bundle that references accumulating collections by LID [\#36](https://github.com/NASA-PDS/deep-archive/issues/36)
- Test Case 3: Bundle that references non-accumulating collections by LID [\#34](https://github.com/NASA-PDS/deep-archive/issues/34)
- Test Case 2: Bundle that references non-accumulating secondary collection by LID or LIDVID [\#33](https://github.com/NASA-PDS/deep-archive/issues/33)
- Test Case 1: Bundle that references non-accumulating collections by LIDVID [\#32](https://github.com/NASA-PDS/deep-archive/issues/32)
- PDS - NSSDCA End-to-end Testing [\#31](https://github.com/NASA-PDS/deep-archive/issues/31)

## [0.1.4](https://github.com/NASA-PDS/deep-archive/tree/0.1.4) (2020-07-02)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.1.3...0.1.4)

## [0.1.3](https://github.com/NASA-PDS/deep-archive/tree/0.1.3) (2020-07-02)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/0.1.2...0.1.3)

**Requirements:**

- The tool shall generate a PDS4 label for the SIP and AIP using at least PDS4 Information Model v1.13.0.0 [\#52](https://github.com/NASA-PDS/deep-archive/issues/52)
- The tool shall include products in the manifests based upon the relationships described in the PDS4 bundle and collection metadata [\#50](https://github.com/NASA-PDS/deep-archive/issues/50)
- The tool shall generate a product manifest based upon the specification of a bundle as input [\#49](https://github.com/NASA-PDS/deep-archive/issues/49)
- The tool shall be capable of generating a valid Archive Information Package transfer manifest and PDS4 XML label in accordance with the PDS4 Information Model [\#45](https://github.com/NASA-PDS/deep-archive/issues/45)

**Defects:**

- AIP Generator outputs duplicate records in the checksum / transfer manifest [\#71](https://github.com/NASA-PDS/deep-archive/issues/71)

## [0.1.2](https://github.com/NASA-PDS/deep-archive/tree/0.1.2) (2020-07-01)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.1.1...0.1.2)

**Defects:**

- Software appears to be excluding all the products associated with the collections [\#69](https://github.com/NASA-PDS/deep-archive/issues/69)

## [v0.1.1](https://github.com/NASA-PDS/deep-archive/tree/v0.1.1) (2020-06-18)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.1.0...v0.1.1)

**Requirements:**

- The tool shall be capable of generating product manifests by crawling a file system using the information contained within the specified bundle and collection products [\#48](https://github.com/NASA-PDS/deep-archive/issues/48)
- The tool shall be capable of generating a valid AIP and SIP products and PDS4 XML label in accordance with the PDS4 Information Model [\#46](https://github.com/NASA-PDS/deep-archive/issues/46)

**Improvements:**

- Update software to handle Document\_File.directory\_path\_name [\#65](https://github.com/NASA-PDS/deep-archive/issues/65)
- Add timestamp to SIP / AIP product LIDs and filenames [\#63](https://github.com/NASA-PDS/deep-archive/issues/63)
- Add READMEs to AIPs and SIPs [\#55](https://github.com/NASA-PDS/deep-archive/issues/55)
- Update software to only include latest collection in when bundle references LIDs [\#24](https://github.com/NASA-PDS/deep-archive/issues/24)
- Document SIP Gen component into Node Delivery procedures [\#8](https://github.com/NASA-PDS/deep-archive/issues/8)

**Defects:**

- Software does not exit after running against large data set [\#64](https://github.com/NASA-PDS/deep-archive/issues/64)
- Update Usage instructions to more clearly define command-line arguments [\#59](https://github.com/NASA-PDS/deep-archive/issues/59)
- AIP Generator not outputting correctly for spice example bundle [\#41](https://github.com/NASA-PDS/deep-archive/issues/41)

**Other closed issues:**

- Updates docs with miniconda alternative installation [\#61](https://github.com/NASA-PDS/deep-archive/issues/61)
- Test Case 4: Bundle that references accumulating collections by LIDVID [\#35](https://github.com/NASA-PDS/deep-archive/issues/35)

## [v0.1.0](https://github.com/NASA-PDS/deep-archive/tree/v0.1.0) (2020-04-24)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/v0.0.1...v0.1.0)

**Defects:**

- SIP label contains invalid manifest URL using file path [\#44](https://github.com/NASA-PDS/deep-archive/issues/44)

## [v0.0.1](https://github.com/NASA-PDS/deep-archive/tree/v0.0.1) (2020-04-23)

[Full Changelog](https://github.com/NASA-PDS/deep-archive/compare/7616dc602beaddda4bb095eab355811fb2beeacb...v0.0.1)

**Improvements:**

- Update docs to include release instructions [\#28](https://github.com/NASA-PDS/deep-archive/issues/28)
- Improve CI/CD to only build off master and PRs and use datetime for PyPi deployment [\#27](https://github.com/NASA-PDS/deep-archive/issues/27)
- Require bundle-base-url when in offline mode [\#22](https://github.com/NASA-PDS/deep-archive/issues/22)
- Develop one script to run both AIP and SIP generator [\#21](https://github.com/NASA-PDS/deep-archive/issues/21)
- Update SIP LID to include bundle version id [\#18](https://github.com/NASA-PDS/deep-archive/issues/18)
- Improve SIP Gen performance for very large data sets [\#13](https://github.com/NASA-PDS/deep-archive/issues/13)

**Defects:**

- SIP Generator not outputting correctly for spice example bundle [\#39](https://github.com/NASA-PDS/deep-archive/issues/39)
- SIP and Transfer Manifest duplicate files and LIDVIDs [\#29](https://github.com/NASA-PDS/deep-archive/issues/29)

**Other closed issues:**

- Test SIP Gen with NSSDC [\#10](https://github.com/NASA-PDS/deep-archive/issues/10)
- Test SIP Gen externally with Discipline Node personnel [\#9](https://github.com/NASA-PDS/deep-archive/issues/9)
- Develop initial AIP generation component [\#3](https://github.com/NASA-PDS/deep-archive/issues/3)
- Implement SIP generation offline capabilities [\#2](https://github.com/NASA-PDS/deep-archive/issues/2)
- Improved user operation and installation guides with github pages [\#1](https://github.com/NASA-PDS/deep-archive/issues/1)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
