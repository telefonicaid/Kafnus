package com.yourcompany;

import io.cucumber.junit.Cucumber;
import io.cucumber.junit.CucumberOptions;
import org.junit.runner.RunWith;

@RunWith(Cucumber.class)
@CucumberOptions(
    features = "src/test/resources/features",
    glue = "com.yourcompany",
    plugin = {
        "pretty",
        "html:target/cucumber-report.html",
        "json:target/cucumber.json"
    }
)
public class TestRunner {
}
