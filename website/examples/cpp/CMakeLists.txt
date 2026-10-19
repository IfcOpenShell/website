cmake_minimum_required(VERSION 3.21)
project(IfcOpenShellWebsiteExamples LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(IfcOpenShell CONFIG REQUIRED)
enable_testing()
set(EXAMPLE_RUN_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/run")
file(MAKE_DIRECTORY "${EXAMPLE_RUN_DIRECTORY}")
configure_file("../fixtures/model.ifc" "${EXAMPLE_RUN_DIRECTORY}/model.ifc" COPYONLY)
foreach(example IN ITEMS Read_walls Edit_a_wall Author_a_model Extract_geometry)
    add_executable(${example} "${example}.cpp")
    target_compile_definitions(${example} PRIVATE BOOST_ALL_NO_LIB)
    target_link_libraries(${example} PRIVATE IfcOpenShell::IfcParse IfcOpenShell::parse_schema_ifc4)
    if(example STREQUAL "Extract_geometry")
        target_link_libraries(${example} PRIVATE IfcOpenShell::IfcGeom IfcOpenShell::geometry_kernel_opencascade)
    endif()
    # Authoring writes model.ifc, so every test gets its own copy of the fixture.
    file(MAKE_DIRECTORY "${EXAMPLE_RUN_DIRECTORY}/${example}")
    configure_file("../fixtures/model.ifc" "${EXAMPLE_RUN_DIRECTORY}/${example}/model.ifc" COPYONLY)
    add_test(NAME ${example} COMMAND "$<TARGET_FILE:${example}>")
    set_tests_properties(${example} PROPERTIES
        WORKING_DIRECTORY "${EXAMPLE_RUN_DIRECTORY}/${example}"
        ENVIRONMENT_MODIFICATION "PATH=path_list_prepend:$<TARGET_FILE_DIR:IfcOpenShell::IfcParse>")
endforeach()
add_custom_target(run_examples
    COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure -C "$<CONFIG>"
    DEPENDS Read_walls Edit_a_wall Author_a_model Extract_geometry
    USES_TERMINAL)
