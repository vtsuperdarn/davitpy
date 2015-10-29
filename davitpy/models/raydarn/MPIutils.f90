! Copyright (C) 2012  VT SuperDARN Lab
! Full license can be found in LICENSE.txt
! A list of useful constants for the ray tracing program
MODULE MPIutils

	use MPI
	implicit none

	integer:: code, nprocs, rank, request, tag

	integer(kind=MPI_OFFSET_KIND):: offset
	integer,dimension(MPI_STATUS_SIZE):: status

	integer:: mpi_size_int, mpi_size_real, mpi_size_vec, mpi_size_param
	integer:: mpi_file_disp
	real(kind=8):: time_init, time_end, time, timeel, timeaz, timehr

END MODULE MPIutils
