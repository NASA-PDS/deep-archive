/*
 * Copyright © 2023, California Institute of Technology ("Caltech").
 * U.S. Government sponsorship acknowledged.
 * 
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * • Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 * • Redistributions must reproduce the above copyright notice, this list of
 * conditions and the following disclaimer in the documentation and/or other
 * materials provided with the distribution.
 * • Neither the name of Caltech nor its operating division, the Jet Propulsion
 * Laboratory, nor the names of its contributors may be used to endorse or
 * promote products derived from this software without specific prior written
 * permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

// Declarative Pipeline
// ====================
//
// This is a Jenkins pipline (of the declarative variety) for continuous deployment of the Deep Archive.
// See https://www.jenkins.io/doc/book/pipeline/syntax/ for more information.

pipeline {

    // We want this to run completely on pds-expo.jpl.nasa.gov and nowhere else
    agent { node('pds-expo') }

    options {
        // Self-explanatory
        disableConcurrentBuilds()
        skipStagesAfterUnstable()
    }

    stages {
        stage('🧱 Build') {
            steps {
                // We might ask the sysadmins to put in a symlink or something like "current"
                sh "/usr/local/python/3.9.16/bin/python3 -m venv .venv"
                sh ".venv/bin/pip install --quiet --upgrade setuptools build wheel pip"
                sh ".venv/bin/pip install --progress-bar off .[dev]"
            }
        }
        stage('🩺 Unit Test') {
            steps {
                sh ".venv/bin/python3 setup.py test"
            }
        }
        stage('🚀 Deploy') {
            steps {
                echo "No-op deploy step: ✓"
            }
        }
        stage('🏃 Integration Test') {
            steps {
                // 🔮 In the future, we'll also want to look at the generated output files and ensure
                // they contain correct data. But right now, pagination is broken in the server so we
                // can't even get output files, so we'll just go by exit status.
                sh ".venv/bin/pds-deep-registry-archive --debug --site PDS_ATM urn:nasa:pds:mer1_navcam_sci_calibrated::1.0"
            }
        }
    }
}
