import os
import sys

# Add parent directory to path to import mri_swarm module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mri_swarm.main import (
    groupchat_mri_analysis,
    mri_swarm,
    batched_mri_swarm,
    mri_agents,
    summary_agent,
)


def assert_equal(expected, actual, message=""):
    """Custom assertion function to check equality"""
    if expected != actual:
        raise AssertionError(f"{message}\nExpected: {expected}\nActual: {actual}")


def assert_type(obj, expected_type, message=""):
    """Custom assertion function to check type"""
    if not isinstance(obj, expected_type):
        raise AssertionError(
            f"{message}\nExpected type: {expected_type}\nActual type: {type(obj)}"
        )


def assert_in(item, container, message=""):
    """Custom assertion function to check containment"""
    if item not in container:
        raise AssertionError(f"{message}\nExpected {item} to be in {container}")


def test_groupchat_mri_analysis():
    """Test the groupchat_mri_analysis function"""
    print("\nTesting groupchat_mri_analysis...")

    # Test with basic task
    task = "Analyze this brain MRI for any abnormalities"
    img = "images/example.jpg"
    result = groupchat_mri_analysis(task=task, img=img)

    # Verify result type and content
    assert_type(result, str, "Result should be a string")
    assert len(result) > 0, "Result should not be empty"

    # Test with multiple images
    imgs = ["images/example.jpg", "images/test.webp"]
    result_multi = groupchat_mri_analysis(task=task, imgs=imgs)
    assert_type(result_multi, str, "Result should be a string")
    assert len(result_multi) > 0, "Result should not be empty"

    print("✓ groupchat_mri_analysis tests passed")


def test_mri_swarm():
    """Test the mri_swarm function"""
    print("\nTesting mri_swarm...")

    # Test basic functionality
    task = "Detect brain lesions"
    img = "images/example.jpg"
    result = mri_swarm(task=task, img=img)
    assert_type(result, str, "Basic result should be a string")
    assert len(result) > 0, "Result should not be empty"

    # Test with additional patient info
    patient_info = "Patient age: 45, symptoms: headache, dizziness"
    result_with_info = mri_swarm(
        task=task, additional_patient_info=patient_info, img=img, return_log=False
    )
    assert_type(result_with_info, str, "Result with patient info should be a string")

    # Test with return_log=True
    result_with_log = mri_swarm(
        task=task, additional_patient_info=patient_info, img=img, return_log=True
    )
    assert_type(result_with_log, dict, "Result with log should be a dictionary")
    required_keys = [
        "id",
        "timestamp",
        "task",
        "number_of_agents",
        "groupchat_analysis",
        "summary",
        "tokens_used",
    ]
    for key in required_keys:
        assert_in(key, result_with_log.keys(), f"Log result should contain key: {key}")

    print("✓ mri_swarm tests passed")


def test_batched_mri_swarm():
    """Test the batched_mri_swarm function"""
    print("\nTesting batched_mri_swarm...")

    # Test data
    tasks = ["Analyze brain MRI for tumors", "Check spine MRI for herniation"]
    patient_infos = ["Patient 1: Age 55, headaches", "Patient 2: Age 42, back pain"]
    imgs = ["images/example.jpg", "images/test.webp"]

    # Test with return_log=True
    results = batched_mri_swarm(
        tasks=tasks, patient_infos=patient_infos, imgs=imgs, return_log=True
    )

    assert_type(results, list, "Batch results should be a list")
    assert_equal(
        len(results), len(tasks), "Number of results should match number of tasks"
    )

    # Test with return_log=False
    results_no_log = batched_mri_swarm(
        tasks=tasks, patient_infos=patient_infos, imgs=imgs, return_log=False
    )

    assert_type(results_no_log, list, "Batch results without log should be a list")
    assert_equal(
        len(results_no_log),
        len(tasks),
        "Number of results should match number of tasks",
    )

    # Test input validation
    try:
        batched_mri_swarm(
            tasks=tasks,
            patient_infos=patient_infos[:-1],  # One less item
            imgs=imgs,
            return_log=True,
        )
        raise AssertionError("Should raise ValueError for mismatched input lengths")
    except ValueError:
        pass  # Expected behavior

    print("✓ batched_mri_swarm tests passed")


def test_agents_configuration():
    """Test the configuration of MRI agents"""
    print("\nTesting agents configuration...")

    # Test number of agents
    assert_equal(len(mri_agents), 5, "Should have 5 specialized agents")

    # Test agent properties
    for agent in mri_agents:
        assert_type(agent.agent_name, str, "Agent name should be string")
        assert_type(agent.agent_description, str, "Agent description should be string")
        assert_type(agent.system_prompt, str, "System prompt should be string")
        assert_equal(agent.max_loops, 1, "Max loops should be 1")
        assert_equal(
            agent.model_name, "claude-3-sonnet-20240229", "Model name should match"
        )
        assert_equal(
            agent.dynamic_temperature_enabled,
            True,
            "Dynamic temperature should be enabled",
        )
        assert_equal(agent.streaming_on, True, "Streaming should be enabled")

    # Test summary agent configuration
    assert_type(summary_agent.agent_name, str, "Summary agent name should be string")
    assert_equal(summary_agent.max_loops, 1, "Summary agent max loops should be 1")
    assert_equal(
        summary_agent.output_type,
        "str-all-except-first",
        "Summary agent output type should match",
    )

    print("✓ Agents configuration tests passed")


def run_all_tests():
    """Run all test functions"""
    print("Running all MRI-Swarm tests...")

    test_agents_configuration()
    test_groupchat_mri_analysis()
    test_mri_swarm()
    test_batched_mri_swarm()

    print("\n✓ All tests passed successfully!")


if __name__ == "__main__":
    run_all_tests()
