program TEMP1D
  implicit none
  real(8) :: Rmin, Rmax, AlfaAir, TempBegin, t1, t2, Tau1, Tau2, C, Ro, K

  ! Dane wejściowe (zamiast z pliku)
  Rmin = 0.0
  Rmax = 0.05
  AlfaAir = 300.0
  TempBegin = 100.0
  t1 = 1200.0
  t2 = 25.0
  C = 700.0
  Ro = 7800.0
  K = 25.0
  Tau1 = 0.0
  Tau2 = 1000.0

  call Temp_1d(Rmin, Rmax, AlfaAir, TempBegin, t1, t2, C, Ro, K, Tau1, Tau2)
end program TEMP1D


subroutine Temp_1d(Rmin, Rmax, AlfaAir, TempBegin, t1, t2, C, Ro, K, Tau1, Tau2)
  implicit none
  real(8), intent(in) :: Rmin, Rmax, AlfaAir, TempBegin, t1, t2, C, Ro, K, Tau1, Tau2
  integer :: nh, ne, i, ie, ip, iTime, Np, nTime
  real(8) :: dTau, Tau, x, dR, a, Alfa, TauMax, dTmax, dT, TempAir, Rp, TpTau
  real(8), dimension(2) :: E, W, N1, N2, r, Fe, TempTau
  real(8), dimension(2, 2) :: Ke
  real(8), allocatable :: vrtxTemp(:), vrtxCoordX(:)
  real(8), allocatable :: aC(:), aD(:), aE(:), aB(:)
  integer :: nPrint

  nh = 51
  ne = nh - 1
  Np = 2
  a = K / (C * Ro)
  E = (/ -0.5773502692d0, 0.5773502692d0 /)
  W = (/ 1.0d0, 1.0d0 /)
  N1 = 0.5d0 * (1.0d0 - E)
  N2 = 0.5d0 * (1.0d0 + E)
    Print *, N1
    Print *, N2
  dR = (Rmax - Rmin) / ne
  dTau = dR ** 2 / (0.5d0 * a)
  TauMax = Tau1 + Tau2
  nTime = int(TauMax / dTau) + 1
  dTau = TauMax / nTime

  allocate(vrtxTemp(nh), vrtxCoordX(nh), aC(nh), aD(nh), aE(nh), aB(nh))

  x = Rmin
  do i = 1, nh
    vrtxCoordX(i) = x
    vrtxTemp(i) = TempBegin
    x = x + dR
  end do

  open(unit=10, file='temperat.txt')
  write(10, *) "Time(s)   T_center   T_surface   dT"
  dTmax = 0.0d0
  Tau = 0.0d0

  do iTime = 1, nTime
    aC = 0.0d0
    aD = 0.0d0
    aE = 0.0d0
    aB = 0.0d0

    TempAir = merge(t2, t1, Tau < Tau1)
    ! Print *, TempAir

    do ie = 1, ne
      r(1) = vrtxCoordX(ie)
      r(2) = vrtxCoordX(ie + 1)
      TempTau(1) = vrtxTemp(ie)
      TempTau(2) = vrtxTemp(ie + 1)
      dR = r(2) - r(1)
      Alfa = 0.0d0
      if (ie == ne) Alfa = AlfaAir

      Ke = 0.0d0
      Fe = 0.0d0

      do ip = 1, Np
        Rp = N1(ip) * r(1) + N2(ip) * r(2)
        TpTau = N1(ip) * TempTau(1) + N2(ip) * TempTau(2)

        Ke(1, 1) = Ke(1, 1) + K * Rp * W(ip) / dR + C * Ro * dR * Rp * W(ip) * N1(ip)**2 / dTau
        Ke(1, 2) = Ke(1, 2) - K * Rp * W(ip) / dR + C * Ro * dR * Rp * W(ip) * N1(ip) * N2(ip) / dTau
        Ke(2, 1) = Ke(1, 2)
        Ke(2, 2) = Ke(2, 2) + K * Rp * W(ip) / dR + C * Ro * dR * Rp * W(ip) * N2(ip)**2 / dTau + 2 * Alfa * Rmax

        Fe(1) = Fe(1) + C * Ro * dR * TpTau * Rp * W(ip) * N1(ip) / dTau
        Fe(2) = Fe(2) + C * Ro * dR * TpTau * Rp * W(ip) * N2(ip) / dTau + 2 * Alfa * Rmax * TempAir
      end do

      aD(ie)     = aD(ie) + Ke(1, 1)
      aD(ie + 1) = aD(ie + 1) + Ke(2, 2)
      aE(ie)     = aE(ie) + Ke(1, 2)
      aC(ie + 1) = aC(ie + 1) + Ke(2, 1)
      aB(ie)     = aB(ie) + Fe(1)
      aB(ie + 1) = aB(ie + 1) + Fe(2)
    end do

    call solve_tridiagonal(nh, aC, aD, aE, aB)

    vrtxTemp = aB
    dT = abs(vrtxTemp(1) - vrtxTemp(nh))
    if (dT > dTmax) dTmax = dT
    write(10, '(F10.2, 3F12.2)') Tau, vrtxTemp(1), vrtxTemp(nh), dT
    Tau = Tau + dTau
  end do

  write(10, *) "dTmax =", dTmax
  close(10)

  deallocate(vrtxTemp, vrtxCoordX, aC, aD, aE, aB)
end subroutine Temp_1d


subroutine solve_tridiagonal(n, a, b, c, d)
  ! Rozwiązuje układ trójdiagonalny: a(i)*x(i-1) + b(i)*x(i) + c(i)*x(i+1) = d(i)
  integer, intent(in) :: n
  real(8), intent(inout) :: a(n), b(n), c(n), d(n)
  real(8) :: m
  integer :: i

  do i = 2, n
    m = a(i) / b(i - 1)
    b(i) = b(i) - m * c(i - 1)
    d(i) = d(i) - m * d(i - 1)
  end do

  d(n) = d(n) / b(n)
  do i = n - 1, 1, -1
    d(i) = (d(i) - c(i) * d(i + 1)) / b(i)
  end do
end subroutine solve_tridiagonal
