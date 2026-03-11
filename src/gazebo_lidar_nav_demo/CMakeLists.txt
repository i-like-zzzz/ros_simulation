cmake_minimum_required(VERSION 3.8)
project(gazebo_lidar_nav_demo)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch urdf worlds maps config models
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
