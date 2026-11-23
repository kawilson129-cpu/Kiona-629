"use strict";

// One shared, standalone script: no backend, imports, credentials or storage.
const priorityForm = document.querySelector("#priority-form");
const policyAreaInput = document.querySelector("#policy-area");
const impactInput = document.querySelector("#impact-level");
const likelihoodInput = document.querySelector("#likelihood-level");
const sensitiveDataInput = document.querySelector("#sensitive-data");
const ongoingIncidentInput = document.querySelector("#ongoing-incident");
const resultContainer = document.querySelector("#result");
const resultContext = document.querySelector("#result-context");
const priorityLabelOutput = document.querySelector("#priority-label");
const calculationOutput = document.querySelector("#calculation");
const scoreCaption = document.querySelector("#score-caption");
const decisionReasonOutput = document.querySelector("#decision-reason");
const nextStepSection = document.querySelector("#next-step-section");
const nextStepOutput = document.querySelector("#next-step");
const formError = document.querySelector("#form-error");
let hasCalculated = false;

// Pure calculation: integer Numbers, multiplication, decisions and Boolean logic.
function calculatePriority(impactLevel, likelihoodLevel, sensitiveData, ongoingIncident) {
  const validNumbers = Number.isInteger(impactLevel) && Number.isInteger(likelihoodLevel);
  const withinRange = impactLevel >= 1 && impactLevel <= 5 && likelihoodLevel >= 1 && likelihoodLevel <= 5;
  if (!validNumbers || !withinRange || typeof sensitiveData !== "boolean" || typeof ongoingIncident !== "boolean") {
    throw new RangeError("Choose valid impact and likelihood values from 1 to 5 and valid context flags.");
  }

  const priorityScore = impactLevel * likelihoodLevel;
  const escalationThreshold = 15;
  const reviewThreshold = 6;
  let priorityLabel;
  let priorityTone;
  let decisionReason;
  let nextStep;

  if (ongoingIncident || (sensitiveData && impactLevel >= 3)) {
    priorityLabel = "Immediate attention";
    priorityTone = "immediate";
    decisionReason = ongoingIncident
      ? "The ongoing-event flag overrides the numerical score."
      : "Sensitive data with impact 3 or above overrides the numerical score.";
    nextStep = "In this practice scenario, promptly contact the established IT or Security channel.";
  } else if (priorityScore >= escalationThreshold) {
    priorityLabel = "High priority";
    priorityTone = "high";
    decisionReason = "The score is at least 15, with no immediate-attention override.";
    nextStep = "In this practice scenario, prioritize a review with the responsible policy owner.";
  } else if (priorityScore >= reviewThreshold) {
    priorityLabel = "Review soon";
    priorityTone = "review";
    decisionReason = "The score is between 6 and 14, with no immediate-attention override.";
    nextStep = "In this practice scenario, arrange a timely clarification with the policy owner.";
  } else {
    priorityLabel = "Routine review";
    priorityTone = "routine";
    decisionReason = "The score is below 6, with no immediate-attention override.";
    nextStep = "In this practice scenario, consult the approved policy and include the concern in a routine review.";
  }

  return { priorityScore, priorityLabel, priorityTone, decisionReason, nextStep };
}

function renderAssessment() {
  // A select's value is a String; Number() supplies actual integer Number inputs.
  const policyArea = policyAreaInput.value;
  const impactLevel = Number(impactInput.value);
  const likelihoodLevel = Number(likelihoodInput.value);
  const sensitiveData = sensitiveDataInput.checked;
  const ongoingIncident = ongoingIncidentInput.checked;

  try {
    const validPolicyArea = Array.from(policyAreaInput.options).some(function (option) {
      return option.value === policyArea;
    });
    if (!validPolicyArea) {
      throw new RangeError("Choose one of the listed policy areas.");
    }
    const assessment = calculatePriority(impactLevel, likelihoodLevel, sensitiveData, ongoingIncident);
    formError.hidden = true;
    formError.textContent = "";
    resultContainer.dataset.priority = assessment.priorityTone;
    resultContext.textContent = policyArea + " · Practice scenario";
    priorityLabelOutput.textContent = assessment.priorityLabel;
    calculationOutput.textContent = impactLevel + " × " + likelihoodLevel + " = " + assessment.priorityScore;
    calculationOutput.hidden = false;
    scoreCaption.hidden = false;
    decisionReasonOutput.textContent = assessment.decisionReason;
    nextStepOutput.textContent = assessment.nextStep;
    nextStepSection.hidden = false;
    hasCalculated = true;

    console.log("DeRexi practice result", {
      policyArea, impactLevel, likelihoodLevel, sensitiveData, ongoingIncident,
      priorityScore: assessment.priorityScore, priorityLabel: assessment.priorityLabel
    });
  } catch (error) {
    clearAssessment();
    formError.textContent = error.message;
    formError.hidden = false;
  }
}

function clearAssessment() {
  hasCalculated = false;
  resultContainer.dataset.priority = "empty";
  resultContext.textContent = "Ready when you are";
  priorityLabelOutput.textContent = "A little context. A clearer next step.";
  calculationOutput.textContent = "";
  calculationOutput.hidden = true;
  scoreCaption.hidden = true;
  decisionReasonOutput.textContent = "Choose your inputs, then calculate to see a priority and its explanation.";
  nextStepOutput.textContent = "";
  nextStepSection.hidden = true;
  formError.textContent = "";
  formError.hidden = true;
}

priorityForm.addEventListener("submit", function (event) {
  event.preventDefault();
  renderAssessment();
});

priorityForm.addEventListener("change", function () {
  // Once calculated, changing any input updates the result rather than leaving it stale.
  if (hasCalculated) {
    renderAssessment();
  }
});

priorityForm.addEventListener("reset", function () {
  clearAssessment();
  policyAreaInput.focus();
});
