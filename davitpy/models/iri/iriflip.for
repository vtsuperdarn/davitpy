C flipiri.for 
C
C 2011.00 10/05/11 IRI-2011: bottomside B0 B1 model (SHAMDB0D, SHAB1D),
C 2011.00 10/05/11    bottomside Ni model (iriflip.for), auroral foE
C 2011.00 10/05/11    storm model (storme_ap), Te with PF10.7 (elteik),
C 2011.00 10/05/11    oval kp model (auroral_boundary), IGRF-11(igrf.for), 
C 2011.00 10/05/11    NRLMSIS00 (cira.for), CGM coordinates, F10.7 daily
C 2011.00 10/05/11    81-day 365-day indices (apf107.dat), ap->kp (ckp),
C 2011.00 10/05/11    array size change jf(50) outf(20,1000), oarr(100).
C 2011.00 12/12/11    Deleted ALT_RATES (not used)

C****************************************************************************************
C subroutines for IDC model
C
C includes: main subroutine CHEMION and the following subroutines and functions
C           KEMPPRN.FOR: CN2D, CNO, CN4S, CN2PLS, CNOP, CO2P, COP4S, COP2D, COP2P,
C                        CNPLS, CN2A, CN2P, CNOPV, TFILE
C           FLIPAP.FOR: FINDAP, RAEDAP, CONV_DATE, GET_DATA
C           RATES.FOR: RATS, RATCHK
C           PESIMP.FOR: SECIPRD, FLXCAL, FACFLX, SIGEXS, TXSION, OXRAT, T_XS_N2, 
C                       T_XS_OX, OXSIGS
C           RSPRIM.FOR: PRIMPR, SCOLUM, PARAMS, PROBS, PROBN2, YLDISS, PROBO2, 
C                       SCHUMN, FACEUV, FACSR, EPHEM SOLDEC, GETLTSZA, ACTUAL_DAY,
C                       BRACE, RUN_ERROR
C 
C Richards, P. G., D. Bilitza, and D. Voglozin (2010), Ion density calculator (IDC): 
C 	A new efficient model of ionospheric ion densities, Radio Sci., 45, RS5007, 
C   doi:10.1029/2009RS004332.
C
C****************************************************************************************
C
C
      SUBROUTINE CHEMION(JPRINT,  !.. Input: Turn file output on or off
     >                      ALT,  !.. Input: Altitude(km)
     >               F107,F107A,  !.. Input: Solar activity indices
     >                 TE,TI,TN,  !.. Input: Electron, ion and neutral temperatures
     >          OXN,O2N,N2N,HEN,  !.. Input: O, O2, N2, and He densities (cm-3)
     >                  USER_NO,  !.. Input: User specified NO density (cm-3)
     >                      N4S,  !.. Input: N4S should be 0.5*MSIS N density (cm-3)
     >                       NE,  !.. Input: electron density (cm-3)
     >               USER_NPLUS,  !.. Input: User specified N+ density (cm-3)
     >                     SZAD,  !.. Input: solar zenith angle(D)
     >     OXPLUS,O2PLUS,NOPLUS,  !.. OUTPUT: O+, O2+, NO+ densities (cm-3)
     >             N2PLUS,NPLUS,  !.. OUTPUT: N2+ and N+ densities (cm-3)
     >                  NNO,N2D,  !.. OUTPUT: NO and N(2D) density (cm-3)
     >                    INEWT)  !.. OUTPUT: Newton procedure fails if INEWT=0
C-------------------------------------------------------------------------------------
C... This routine was written by Phil Richards April 2010. 
C... It takes the specified input electron density and returns O+, O2+, NO+,
C... N2+, N+, NO, and N(2D) densities.These densities generally agree well
C... with the FLIP model densities.
C... All the densities except O+ are calculated from chemical equilibrium.
C... O+ is calculated using a Newton iterative procedure so that the total 
C... ion density matches the input electron density.
C... N+ and NO densities can either be user specified or calculated by the model.
C... N+ generally agrees well with AE-C data and the FLIP model during the day, 
C... but is inaccurate at night due to lack of diffusion.
C... NO will be very good except below about 130 km where it will be 
C... underestimated due to neglect of diffusion. There is an artificial 
C... floor on the NO density to prevent it from getting too low below 130 km.
C... If the Newton procedure fails to converge, all ions including O+ are 
C... calculated from chemical equilibrium and then normalized to reproduce 
C... the input electron density. This generally works well.
C... The Newton procedure usually works if the total calculated molecular ion 
C... densities do not approach the input electron density. Difficulties are most   
C... likely to happen below ~150 km and especially at night. A Newton solution is 
C... usually found when the O+ density is not too much smaller than the modeled 
C... molecular ion density.
C... The EUVAC model is used for solar EUV irradiances
C-------------------------------------------------------------------------------------
      IMPLICIT NONE
      INTEGER JPRINT        !.. Turns on printing of production and loss
      INTEGER INEWT         !.. Signifies when the Newton procedure fails
      INTEGER I,J,K,ITERS   !.. loop control variables
      INTEGER IRATS         !.. Switch for different rates
      INTEGER ITS,JITER     !.. Variables for Newton procedure
      REAL TE,TN,TI         !.. Electron and ion temperatures
      !.. Geophysical parameters
      REAL F107,F107A,ALT,SZAD
      !.. Measured H+, He+, O+, N2+, NO+, O2+, N+, RPA ion density
      REAL HEPLUS,OXPLUS,N2PLUS,NOPLUS,O2PLUS,NPLUS,USER_NPLUS
      !.. O2,O,N2,NO,He,N4S, user specified NO
      REAL O2N,OXN,N2N,NNO,HEN,N4S,USER_NO
      !.. Ne, N(2P),N(2D),O+(2P),O+(2D) densities
      REAL NE,N2P,N2D,OP2D,OP2P
      !.. Total (photon & photoel) production rates O+(4S),O+(2P),O+(2D),O2+
      REAL TPROD1,PDISOP,TPROD2,TPROD3,TPROD5
      !.. Total Production rates from all sources for NO+, O2+, 
      REAL TPNOP,O2PPROD
      !.. Production rates hv(e*)+N2->N+, hv+N->N+, Lyman-a -> NO+ 
      REAL DISNP,PHOTN,PLYNOP
      REAL PSEC                     !.. generic PE production
      REAL RTS(99)                  !.. Reaction rates array
      REAL SECPN2PLUS,EUVN2PLUS     !.. N2+ total production
      REAL H,DEX,FEX(2)             !.. used in Newton solver
      REAL SUMIONS                  !.. Sum of the major ions
      REAL PNO,LNO,PDNOSR           !.. Production and loss of NO
      REAL N2A                      !.. N2(A) density    
      REAL VCON                     !.. FLIP N2(v) factor. Not used here
      REAL DISN2D,UVDISN,PN2D,LN2D  !.. Production and loss of N(2D)
      REAL ALTCHEM                  !.. altitude for chemistry calculation
      REAL N2APRD                   !.. PE production rate of N2(A)
      REAL PN4S,LN4S,DISN4S
      REAL OXPLUSAVE
      !.. various ionization and excitation rates by EUV and PE
      REAL EUVION,PEXCIT,PEPION,OTHPR1,OTHPR2
      COMMON/EUVPRD/EUVION(3,12),PEXCIT(3,12),PEPION(3,12),OTHPR1(6)
     >   ,OTHPR2(6)

      !.. initialize parameters
      DATA VCON/1.0/K/0/
      DATA PNO,LNO,PDNOSR,PLYNOP,N2A/5*0.0/
      DATA DISN2D,UVDISN/0.0,0.0/
      DATA HEPLUS/0.0/
!       print*, JPRINT,ALT,F107,F107A,TE,TI,TN,OXN,O2N,N2N,HEN,USER_NO,N4S,NE,USER_NPLUS,SZAD

      ALTCHEM=150  !.. Initial altitude for O+ for imposing chemistry
      JITER=0      !.. Counts the number of Newton iterations
      N2P=0.0      !.. N(2P) density

      CALL RATS(0,TE,TI,TN,RTS)  !.. Get the reaction rates

      !.. PRIMPR calculates solar EUV production rates. 
      CALL PRIMPR(1,ALT,OXN,N2N,O2N,HEN,SZAD*0.01745,TN,F107,F107A,N4S)
      UVDISN=OTHPR1(1)

      !.. Calculate secondary Production from photoelectrons
      CALL SECIPRD(ALT,SZAD,F107,F107A,TE,TN,OXN,O2N,N2N,NE,N2APRD)

      DISNP= EUVION(3,4)+EUVION(3,5)+EUVION(3,6)
     >   +0.1*(PEPION(3,1)+PEPION(3,2)+PEPION(3,3))  !.. Rydberg diss       
     >   +PEPION(3,4)+PEPION(3,5)+PEPION(3,6)       
      DISN2D=2.0*PEPION(3,1)+OTHPR2(3)
      DISN4S=2.0*PEPION(3,1)+OTHPR2(3)
   
      !**********  Come back here if Newton fails
 5    CONTINUE 
        !.. initialize variables to avoid using left over values
        HEPLUS=0.0
        OXPLUS=0.0
        N2PLUS=0.0
        NOPLUS=0.0
        O2PLUS=0.0
        NPLUS=0.0
        N2P=0.0
        N2D=0.0
        OP2D=0.0
        OP2P=0.0
        N2A=0.0

      !.. Iterate through chemistry twice in case O+ is chemical equilibrium
      DO ITERS=1,3
        !.. K counts number of iterations for printing headers in routines
        K=K+1 
        !.. Set initial value for electron density 
        !.. O+(2P) Calculate and print densities, production, loss
        PSEC=PEPION(1,3)           !.. Photoelectron production
        TPROD3=EUVION(1,3)+PSEC    !.. Add EUV and photoelectrons
        CALL COP2P(JPRINT,7,K,ALT,RTS,OXN,O2N,N2N,NE,OP2P,TPROD3,PSEC
     >    ,HEPLUS,N4S,NNO,TE)

        !.. O+(2D) Calculate and print densities, production, loss
        PSEC=PEPION(1,2)           !.. Photoelectron production
        TPROD2=EUVION(1,2)         !.. EUV
        CALL COP2D(JPRINT,8,K,ALT,RTS,OXN,O2N,N2N,NE,OP2D,TPROD2,OP2P
     >    ,HEPLUS,N4S,NNO,PSEC)

        !.. O+(4S) Calculate and print densities, production, loss. 
        TPROD1=EUVION(1,1)
        PDISOP=EUVION(2,4)+EUVION(2,5)+PEPION(2,4)+PEPION(2,5)
        CALL COP4S(JPRINT,4,K,ALT,RTS,OXN,O2N,N2N,NE,OXPLUS,TPROD1,OP2D
     >    ,OP2P,PEPION(1,1),PDISOP,N2PLUS,N2D,NNO,1.0,HEPLUS)

        CALL CN2A(JPRINT,27,K,ALT,RTS,OXN,O2N,N2N,NE,N2A,N2APRD,0.0,
     >     0.0,0.0)

        !..CALL CN2P(JPRINT,0,K,ALT,RTS,OXN,O2N,N2N,NE,PN2P,LN2P
        !..> ,N2P,P3X7,UVDISN,O2PLUS,NNO,N2PLUS)

        !.. N(2D) Calculate and print densities, production, loss. 
        CALL CN2D(JPRINT,16,K,ALT,RTS,OXN,O2N,N2N,NOPLUS,NE,PN2D,LN2D
     >    ,N2PLUS,DISN2D,UVDISN,NPLUS,N2P,N2D,OXPLUS,NNO,N2A)
        N2D=PN2D/LN2D

        !.. N2+ Calculate and print densities, production, loss. 
        CALL CN2PLS(JPRINT,9,K,ALT,RTS,OXN,O2N,N2N,NE,N2PLUS,EUVION(3,1)
     >   ,EUVION(3,2),EUVION(3,3),PEPION(3,1),PEPION(3,2),PEPION(3,3)
     >   ,OP2D,OP2P,HEPLUS,NPLUS,NNO,N4S)

        !.. N+ Calculate and print densities, production, loss. 
        !.. Note that N(2D) is turned off in N+ solution 
        PHOTN=OTHPR2(3)  !.. N+ prod
        CALL CNPLS(JPRINT,10,K,ALT,RTS,OXN,O2N,N2N,NE,DISNP,NPLUS,
     >    OXPLUS,N2D,OP2P,HEPLUS,PHOTN,O2PLUS,N4S,OP2D,N2PLUS,NNO)
        IF(USER_NPLUS.GT.0) NPLUS=USER_NPLUS  !.. User specified N+

        CALL CN4S(JPRINT,28,K,ALT,RTS,OXN,O2N,N2N,NE,PN4S,LN4S,N4S,
     >    DISN4S,N2D,N2P,OXPLUS,N2PLUS,UVDISN,NOPLUS,NPLUS,NNO,
     >    O2PLUS,PDNOSR,1.0)
          !..N4S=PN4S/LN4S

        !.. NO Calculate and print densities, production, loss.
        CALL CNO(JPRINT,15,K,ALT,RTS,OXN,O2N,N2N,NE,PNO,LNO
     >    ,N2D,N4S,N2P,NNO,O2PLUS,OXPLUS,OTHPR2(2),OTHPR2(1),N2A,NPLUS)
        
        NNO=PNO/LNO     !.. NO chemical equilibrium density
        !.. Set a floor on NO density, which is needed below ~150 km at night 
        IF(NNO.LT.1.0E8*EXP((100-ALT)/20)) NNO=1.0E8*EXP((100-ALT)/20)
        IF(USER_NO.GT.1.0) NNO=USER_NO  !.. substitute user specified value
        IF(NNO.GT.1.5E8) NNO=1.5E8      !.. Don't let NO get too big

        !.. NO+ Calculate and print densities, production, loss. 
        CALL CNOP(JPRINT,11,K,ALT,RTS,OXN,O2N,N2N,NE,TPNOP,NOPLUS,OXPLUS
     >    ,N2PLUS,O2PLUS,N4S,NNO,NPLUS,N2P,PLYNOP,VCON,N2D,OP2D)

        !.. O2+ Calculate and print densities, production, loss. 
        !.. EUV + PE production
        TPROD5=EUVION(2,1)+EUVION(2,2)+EUVION(2,3)+PEPION(2,1)+
     >       PEPION(2,2)+PEPION(2,3)
        CALL CO2P(JPRINT,12,K,ALT,RTS,OXN,O2N,N2N,NE,O2PPROD
     >    ,O2PLUS,TPROD5,OXPLUS,OP2D,N2PLUS,NPLUS,N4S,NNO,OP2P)
      ENDDO

      !.. This section for chemical equilibrium densities for all species 
      !.. including O+. It is used when the Newton procedure fails to get O+
      !.. Don't bother if molecular ions greater than Ne/2
      !.. It increments ALTCHEM to force this action. The ion densities are 
      !.. normalized to the input NE. N+ is excluded in case it is user specified
      INEWT=1
      SUMIONS=OXPLUS+NOPLUS+O2PLUS+NPLUS
      IF(ALT.LT.ALTCHEM.OR.NOPLUS+O2PLUS.GT.0.85*NE) THEN
         OXPLUS=OXPLUS*NE/SUMIONS
         NOPLUS=NOPLUS*NE/SUMIONS
         O2PLUS=O2PLUS*NE/SUMIONS
         NPLUS=NPLUS*NE/SUMIONS
         INEWT=0
         RETURN
      ENDIF

      !.. Newton solution for O+ density given the electron density (NE)
      !.. Go through twice to set up the derivative (F(x+h)-F(x))/h
      !.. First O+ guess for Newton. This is important for high altitudes
      !.. because Newton may converge on first try.
      OXPLUSAVE=OXPLUS
      IF(NE-NOPLUS-O2PLUS.GT.100) OXPLUS=NE-NOPLUS-O2PLUS
      !..IF(SZAD.GT.89) OXPLUS=NE  !.. first guess at night    
 9    DO ITS=1,2
        IF(ITS.EQ.1) H=OXPLUS*0.0001         !.. increment for dn/dt
        IF(ITS.EQ.2) OXPLUS=OXPLUS+H       !.. increment N

        !.. N+ Calculate and print densities, production, loss. 
        CALL CNPLS(JPRINT,10,K,ALT,RTS,OXN,O2N,N2N,NE,DISNP,NPLUS,
     >    OXPLUS,N2D,OP2P,HEPLUS,PHOTN,O2PLUS,N4S,OP2D,N2PLUS,NNO)
        IF(USER_NPLUS.GT.0) NPLUS=USER_NPLUS  !.. User specified N+

        !.. N2+ Calculate and print densities, production, loss. 
        CALL CN2PLS(JPRINT,9,K,ALT,RTS,OXN,O2N,N2N,NE,N2PLUS,EUVION(3,1)
     >    ,EUVION(3,2),EUVION(3,3),PEPION(3,1),PEPION(3,2),PEPION(3,3)
     >    ,OP2D,OP2P,HEPLUS,NPLUS,NNO,N4S)

        !.. NO+ Calculate and print densities, production, loss. 
        CALL CNOP(JPRINT,11,K,ALT,RTS,OXN,O2N,N2N,NE,TPNOP,NOPLUS,OXPLUS
     >   ,N2PLUS,O2PLUS,N4S,NNO,NPLUS,N2P,PLYNOP,VCON,N2D,OP2D)

        !.. O2+ Calculate and print densities, production, loss. 
        !.. EUV + PE production
        TPROD5=EUVION(2,1)+EUVION(2,2)+EUVION(2,3)+PEPION(2,1)+
     >     PEPION(2,2)+PEPION(2,3)
        CALL CO2P(JPRINT,12,K,ALT,RTS,OXN,O2N,N2N,NE,O2PPROD
     >    ,O2PLUS,TPROD5,OXPLUS,OP2D,N2PLUS,NPLUS,N4S,NNO,OP2P)

        !.. N(2D) Calculate and print densities, production, loss. 
        CALL CN2D(JPRINT,16,K,ALT,RTS,OXN,O2N,N2N,NOPLUS,NE,PN2D,LN2D
     >     ,N2PLUS,DISN2D,UVDISN,NPLUS,N2P,N2D,OXPLUS,NNO,N2A)
        N2D=PN2D/LN2D

        !.. calculation of F(x) from the total ion concentration
        FEX(ITS)=OXPLUS+NOPLUS+O2PLUS+N2PLUS+NPLUS-NE
      ENDDO
        
      !.. Test for convergence and add increment to O+ if not
      JITER=JITER+1          !.. for stopping the iterations
      DEX=(FEX(2)-FEX(1))/H
      OXPLUS=OXPLUS-H-FEX(1)/DEX

      !.. If Newton fails, go back and calculate O+ chem equilibrium
      IF(JITER.GT.6.OR.OXPLUS.LT.0.0.OR.OXPLUS.GT.1.0E7) THEN
        ALTCHEM=ALT+1  !.. forces chemical equilibrium densities
        GOTO 5         !.. Go back to chemical eqilibrium
      ENDIF     

      !.. Test for convergence
      SUMIONS=OXPLUS+NOPLUS+O2PLUS+N2PLUS+NPLUS
      IF(ABS((NE-SUMIONS)/NE).GT.0.05) GOTO 9

      !.. Normalize ion densities to the input electron density
      OXPLUS=OXPLUS*NE/SUMIONS
      NOPLUS=NOPLUS*NE/SUMIONS
      O2PLUS=O2PLUS*NE/SUMIONS
      NPLUS=NPLUS*NE/SUMIONS

      !.. If O+ a very minor ion, Newton solution may not be good, force  
      !.. chemical equilibrium solution instead
      IF(OXPLUS/SUMIONS.LT.0.1) THEN
        ALTCHEM=ALT+1  !.. forces chemical equilibrium densities
	  GOTO 5         !.. Go back to chemical eqilibrium
      ENDIF
      RETURN
      END
C
C
C.................... KEMPRN.FOR ......................................   
C.. This file contains the chemistry routines for ions and neutrals
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CN2D(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NOP,NE,P1,L1
     > ,N2PLS,DISN2D,UVDISN,NPLUS,N2P,N2D,OPLS,NNO,N2A)
C.......n(2d)
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=NOP*NE*RTS(50)
      PR(2)=N2PLS*NE*RTS(32)*RTS(11)
      PR(3)=N2PLS*ON*RTS(10)
      PR(4)=DISN2D
      PR(5)=RTS(63)*UVDISN
      PR(6)=RTS(65)*NPLUS*O2N
      PR(7)=N2P*RTS(57)
      PR(8)=RTS(27)*N2A*ON
      LR(1)=ON*RTS(15)
      LR(2)=O2N*RTS(16)
      LR(3)=NE*RTS(8)
      LR(4)=OPLS*RTS(29)
      LR(5)=RTS(61)
      LR(6)=RTS(41)*NNO
      P1=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)
      L1=LR(1)+LR(2)+LR(3)+LR(4)+LR(5)+LR(6)
C....... EF is used to convert production rates to volume emission rates
      EF=1.0
C....... This line in for volume emission rates
C...      EF=RTS(61)*0.76/L1
      IF(JPT.EQ.1.AND.JPR.GT.0.AND.INT(EF+0.1).NE.1) WRITE(I,189)
      IF(JPT.EQ.1.AND.JPR.GT.0.AND.INT(EF+0.1).EQ.1) WRITE(I,191)
 189  FORMAT(/2X,'N(2D)',25X,'EMISSION',28X,':',20X,'Loss rate')
 191  FORMAT(/2X,'N(2D)',25X,'Production',36X,':',20X,'Loss rate')
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,96)
 96   FORMAT(2X,'ALT   [N2D]   NO++e   N2++e   N2++O    e+N2   hv+N2'
     >  ,3X,'N++O2   N(2P)   N2A+O    +O     +O2      +e     +O+'
     >  ,5X,'RAD     +NO')
      IF(JPR.GT.0) WRITE(I,7) Z,P1/L1,(PR(K)*EF,K=1,8)
     > ,(LR(K)*N2D,K=1,6)
      RETURN
 7    FORMAT(F6.1,1P,22E8.1)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CNO(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,P1,L1
     > ,N2D,N4S,N2P,NNO,O2P,OPLS,PDNOSR,PLYNOP,N2A,NPLUS)
C........no
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=RTS(16)*O2N*N2D
      PR(2)=RTS(7)*O2N*N4S
      PR(3)=RTS(38)*N2P*O2N
      PR(4)=RTS(27)*N2A*ON
      PR(5)=RTS(22)*NPLUS*O2N          !.. Fox
      LR(1)=RTS(9)*N4S
      LR(2)=RTS(23)*O2P
      LR(3)=RTS(24)*OPLS
      LR(4)=RTS(41)*N2D
      LR(5)=PDNOSR
      LR(6)=PLYNOP
      P1=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)
      L1=LR(1)+LR(2)+LR(3) + LR(4) + (LR(5)+LR(6))
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,192)
 192   FORMAT(/2X,'NO',17X,'PRODUCTION',20X,':',10X,'LOSS RATES'/
     > ,4X,'ALT',3X,'[NO]',5X,'[NO]c',3X,'O2+N2D',
     > 3X,'O2+N4S   N2P+O2   N2A+O    N++O2    N4S+NO   O2P+NO   O++NO'
     > ,3X,'N2D+NO   hv<1910   Lyman-a')
      IF(JPR.GT.0) WRITE(I,7) Z,NNO,P1/L1,(PR(K),K=1,5)
     > ,(LR(K)*NNO,K=1,6)
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CN4S(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,P1,L1,N4S,DISN4S
     >   ,N2D,N2P,OPLS,N2PLS,UVDISN,NOP,NPLUS,NNO,O2P,PDNOSR,VCON)
C........N(4S)
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=DISN4S
      PR(2)=RTS(15)*ON*N2D
      PR(3)=RTS(8)*NE*N2D
      PR(4)=VCON*RTS(3)*OPLS*N2N
      PR(5)=RTS(53)*RTS(11)*N2PLS*NE
      PR(6)=RTS(62)*UVDISN
      PR(7)=NOP*NE*RTS(49)
      PR(8)=N2D*RTS(61)
      PR(9)=N2P*RTS(58)
      PR(10)=RTS(25)*NPLUS*O2N
      PR(11)=PDNOSR*NNO
      PR(12)=NPLUS*NNO*RTS(81)      !..Fox
      LR(1)=RTS(7)*O2N
      LR(2)=RTS(9)*NNO
      LR(3)=RTS(21)*O2P
      LR(4)=RTS(79)*N2PLS     !..Fox
      P1=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)+PR(9)+PR(10)
     >     +PR(11)+PR(12)
      L1=LR(1)+LR(2)+LR(3)+LR(4)
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,193)
 193   FORMAT(/2X,'N(4S)',38X,'PRODUCTION',46X,':',7X,'LOSS RATES'/
     > ,3X,'ALT',2X,'[N4S]',2X,'hv->N+'
     > ,3X,'O+N2D',2X,'e+N2D',3X,'O++N2',3X,'N2++e',4X,'hv->2N'
     > ,2X,'NO++e',2X,'N(2D)',4X,'N(2P)   N+&X    hv+NO    +O2  '
     > ,2X,' +NO  ',2X,'+O2+ & N2+')
      PR(10)=PR(10)+PR(12)  !... for printing fit
      LR(3)=LR(3)+LR(4)     !... for printing fit
      IF(JPR.GT.0) WRITE(I,7) Z,N4S,(PR(K),K=1,11),(LR(K)*N4S,K=1,3)
      RETURN
 7    FORMAT(F6.1,1P,22E8.1)
      END
C::::::::::::::::::::::::::::::: CN2PLS :::::::::::::::::::::::::::::::
C..... Simplified chemistry of N2+.  PUN2P* = production of N2+ by euv 
C..... in the (X,A,B states). PEN2P* same for p.e.s (X,A,B states)
      SUBROUTINE CN2PLS(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,N2PLS,PUN2PX,
     >  PUN2PA,PUN2PB,PEN2PX,PEN2PA,PEN2PB,OP2D,OP2P,HEPLUS,NPLUS,
     >  NNO,N4S)
      IMPLICIT REAL(A-H,L,N-Z)
      REAL PUN2PX,PUN2PA,PUN2PB,PEN2PX,PEN2PA,PEN2PB
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=PUN2PX
      PR(2)=PUN2PA
      PR(3)=PUN2PB
      PR(4)=PEN2PX
      PR(5)=PEN2PA
      PR(6)=PEN2PB
      PR(7)=RTS(19)*OP2D*N2N
      PR(8)=RTS(20)*OP2P*N2N
      PR(9)=RTS(44)*HEPLUS*N2N
      PR(10)=RTS(82)*NPLUS*NNO   !..Fox
      LR(1)=RTS(10)*ON
      LR(2)=RTS(11)*NE
      LR(3)=RTS(17)*O2N
      LR(4)=RTS(99)*ON
      LR(5)=RTS(79)*N4S     !..Fox
      LR(6)=RTS(80)*NNO     !..Fox
      N2PLS=
     >  (PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)+PR(9)+PR(10))/
     >  (LR(1)+LR(2)+LR(3)+LR(4)+LR(5)+LR(6))
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,95)
 95   FORMAT(/2X,'N2+',29X,'PRODUCTION',45X,':',12X,'LOSS RATES'/
     > ,3X,'ALT  [N2+]  EUV-X   EUV-A    EUV-B   PE-X'
     > ,5X,'PE-A    PE-B  O+2D+N2  O+2P+N2  He++N2  O+N2+'
     > ,2X,'e+N2+  O2+N2+  N2++O  Other')
      PR(9)=PR(9)+PR(10)     !.. for printing fit
      LR(5)=LR(5)+LR(6)      !.. for printing fit
      IF(JPR.GT.0) WRITE(I,7) Z,N2PLS,(PR(K),K=1,9)
     > ,(LR(K)*N2PLS,K=1,5)
      RETURN
 7    FORMAT(F6.1,1P,22E8.1)
      END
C:::::::::::::::::::::::::::::: CNOP ::::::::::::::::::::::::::::::::::
      SUBROUTINE CNOP(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,P1,NOP,OPLS
     >  ,N2PLS,O2P,N4S,NNO,NPLUS,N2P,PLYNOP,VCON,N2D,OP2D)
C........no+
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=VCON*RTS(3)*N2N*OPLS
      PR(2)=N2PLS*ON*RTS(10)
      PR(3)=O2P*N4S*RTS(21)
      PR(4)=O2P*NNO*RTS(23)
      !.. N+ + O2 -> O2+ + N(2D,4S) or NO+ + O(1S)
      PR(5)=(RTS(30)+RTS(66)+RTS(59))*NPLUS*O2N
      PR(6)=RTS(37)*N2P*ON
      PR(7)=RTS(24)*OPLS*NNO
      PR(8)=PLYNOP*NNO
      PR(9)=O2P*N2D*RTS(77)         !..Fox
      PR(10)=N2PLS*NNO*RTS(80)      !..Fox
      PR(11)=NPLUS*NNO*RTS(81)      !..Fox
      PR(12)=RTS(83)*NNO*OP2D       !..Fox
      PR(13)=OP2D*RTS(90)*N2N        !.. -> NO+ + N, Li et al. [1997] 
      LR(1)=NE*RTS(5)
      P1=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)
     >    +PR(9)+PR(10)+PR(11)+PR(12)+PR(13)
      NOP=P1/LR(1)

      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,96)
 96   FORMAT(/2X,'NO+',31X,'PRODUCTION',48X,':',2X,'LOSS RATES'/
     > ,3X,'ALT',3X,'[NO+]',4X,'O++N2',3X,'N2++O',3X,'O2++N4S'
     > ,3X,'O2++NO',3X,'N++O2',4X,'N2P+O',3X,'O++NO   hv+NO'
     > ,5X,'O2++N2D   N2++NO   N++NO   OP2D+NO   OP2D+N2  NO++e')
      !PR(9)=PR(9)+PR(10)+PR(11)+PR(12)+PR(13)
      IF(JPR.GT.0) WRITE(I,7) Z,NOP,(PR(K),K=1,13),LR(1)*NOP
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CO2P(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,P1
     > ,O2P,TPROD5,OPLS,OP2D,N2PLS,NPLUS,N4S,NNO,OP2P)
C........o2+
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
C......... TPROD5=euv @ p.e. production
      PR(1)=TPROD5
      PR(2)=RTS(4)*O2N*OPLS
      PR(3)=RTS(43)*OP2D*O2N
      PR(4)=RTS(17)*O2N*N2PLS
      PR(5)=RTS(25)*NPLUS*O2N
      PR(6)=RTS(86)*OP2P*O2N           !.. Fox
      PR(7)=RTS(65)*NPLUS*O2N
      LR(1)=RTS(6)*NE
      LR(2)=RTS(21)*N4S
      LR(3)=RTS(23)*NNO
      P1=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)
      O2P=P1/(LR(1)+LR(2)+LR(3))
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,97)
  97  FORMAT(/2X,'O2+',22X,'PRODUCTION',24X,':',12X,'LOSS RATES'
     > /,3X,'ALT',3X,'[O2+]',3X,'hv+O2',3X,'O++O2',3X,'O+(2D)+O2'
     >  ,4X,'N2++O2   N++O2   O+(2P)+O2  O2++e   O2++N   O2++NO')
      IF(JPR.GT.0) WRITE(I,7) Z,O2P,(PR(K),K=1,7),(LR(K)*O2P,K=1,3)
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE COP4S(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,OPLS,TPROD1,OP2D
     >  ,OP2P,PEPION,PDISOP,N2PLS,N2D,NNO,VCON,HEPLUS)
C...........o+(4s)
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
C.........pr(1)= euv production of o+(4s)
      PR(1)=TPROD1
      PR(2)=OP2D*NE*RTS(12)
      PR(3)=OP2P*ON*RTS(26)
      PR(4)=PEPION
      PR(5)=PDISOP
      PR(6)=RTS(99)*N2PLS*ON
      PR(7)=OP2P*NE*RTS(14)
      PR(8)=OP2P*0.047
      PR(9)=RTS(28)*ON*OP2D
      PR(10)=RTS(85)*OP2P*O2N              !.. Fox
      PR(11)=HEPLUS*O2N*(RTS(91)+RTS(93))  !..Fox
      PR(12)=RTS(95)*NNO*HEPLUS            !..Fox
      !PR(13)=RTS(22)*NPLUS*O2N             !..Fox
      LR(1)=N2N*VCON*RTS(3)
      LR(2)=O2N*RTS(4)
      LR(3)=NNO*RTS(24)
      LR(4)=N2D*RTS(29)    !.... small loss?? ..Fox
      !..LR(4)=(LR(1)+LR(2)+LR(3))  !.. total loss for printing
      PR(10)=PR(10)+PR(11)+PR(12)+PR(13)
      PRTOT=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)+PR(9)+PR(10)
      LRTOT=LR(1)+LR(2)+LR(3)+LR(4)
      OPLS=PRTOT/LRTOT
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,98)
 98   FORMAT(/2X,'O+',41X,'PRODUCTION',39X,':',10X,'LOSS RATES'/
     >  ,' ALT    [O+]   hv+O  O+(2D)+e O+(2P)+O   e*+O  O2-diss  '
     >  ,'N2++O  O+(2P)+e O+(2P) O+O+(2D)   Other  +N2     +O2    '
     >  ,'+NO   +N2D')
      IF(JPR.GT.0) WRITE(I,7) Z,OPLS,(PR(K),K=1,10)
     > ,(LR(K)*OPLS,K=1,4)
      RETURN
 7    FORMAT(F6.1,1P,22E8.1)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE COP2D(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,OP2D,TPROD2,OP2P
     > ,HEPLUS,N4S,NNO,PSEC)
C.......o+(2d)
      IMPLICIT REAL (A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=TPROD2                ! EUV  prod
      PR(2)=OP2P*NE*RTS(13)
      PR(3)=OP2P*0.171
      PR(4)=HEPLUS*O2N*RTS(76)     !..Fox
	PR(5)=PSEC
      LR(1)=RTS(19)*N2N
      LR(2)=7.7E-5                 !.. radiation at 3726 and 3729 A
      LR(3)=NE*RTS(12)
      LR(4)=ON*RTS(28)
      LR(5)=RTS(43)*O2N
      LR(6)=RTS(83)*NNO      !..Fox
      LR(7)=RTS(84)*N4S      !..Fox
      LR(8)=RTS(90)*N2N      !.. -> NO+ + N, Li et al. [1997] 
      OP2D=(PR(1)+PR(2)+PR(3)+PR(4)+PR(5))/
     >   (LR(1)+LR(2)+LR(3)+LR(4)+LR(5)+LR(6)+LR(7)+LR(8))
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,99)
 99   FORMAT(/2X,'O+(2D)',13X,'PRODUCTION',27X,':',18X,'LOSS RATES'/
     > ,3X,'ALT',3X,'[O+2D]',3X,'hv+O',4X,'e*+O',4X,'O+2P+e',3X,
     > 'O+2P>hv',2X,'He++O2     +N2    E3726_29    +e       +O      +O2'
     > '      +NO     +N  +N2>NO+')
      IF(JPR.GT.0) WRITE(I,7) Z,OP2D,PR(1),PR(5),PR(2),PR(3),PR(4)
     > ,(LR(K)*OP2D,K=1,8)
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE COP2P(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,OP2P,TPROD3,PSEC
     > ,HEPLUS,N4S,NNO,TE)
C.......o+(2p)
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=0.0
      IF(TPROD3.GE.PSEC) PR(1)=TPROD3-PSEC
      PR(2)=PSEC
      PR(3)=HEPLUS*O2N*RTS(92)        !..Fox
      LR(1)=RTS(26)*ON
      LR(2)=RTS(20)*N2N
      LR(3)=RTS(13)*NE
      LR(4)=0.218
      LR(5)=RTS(14)*NE
      LR(6)=(RTS(85)+RTS(86))*O2N    !..Fox
      LR(7)=RTS(87)*N4S              !..Fox
      LR(8)=RTS(88)*NNO              !..Fox
      OP2P=(TPROD3+PR(3))
     >  /(LR(1)+LR(2)+LR(3)+LR(4)+LR(5)+LR(6)+LR(7)+LR(8))
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,100)
 100   FORMAT(/2X,' O+(2P)',6X,'PRODUCTION',10X,':',12X,'LOSS RATES'/
     >,3X,'ALT   [O+2P]    hv+O     e*+O  He++O2      +O',7X,'+N2'
     > ,6x,'+e       RAD      +e      +O2      +N4S     +NO'
     > ,6x,'OX       N2        e      Te       E7320')
      IF(JPR.GT.0) WRITE(I,7) Z,OP2P,PR(1),PR(2),PR(3),
     >  (LR(K)*OP2P,K=1,8),ON,N2N,NE,TE,OP2P*0.218*0.781
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CNPLS(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,DISNP
     > ,NPLUS,OPLS,N2D,OP2P,HEPLUS,PHOTN,O2P,N4S,OP2D,N2PLS,NNO)
C........n+
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=DISNP
      PR(2)=RTS(29)*OPLS*N2D
      PR(3)=0
      PR(4)=RTS(45)*HEPLUS*N2N
      PR(5)=PHOTN
      PR(6)=O2P*N2D*RTS(78)          !..Fox
      PR(7)=N2PLS*N4S*RTS(79)        !..Fox
      PR(8)=OP2D*N4S*RTS(84)         !..Fox
      PR(9)=RTS(94)*NNO*HEPLUS       !..Fox
      LR(1)=RTS(30)*O2N              !..Fox
      LR(2)=RTS(25)*O2N              !..Fox
      LR(3)=RTS(22)*O2N              !..Fox
      LR(4)=RTS(65)*O2N              !..Fox
      LR(5)=RTS(66)*O2N              !..Fox
      LR(6)=RTS(31)*ON               !..Fox

      CNPLUS=0.0
      IF(LR(1)+LR(2)+LR(3).GT.0.0)
     >CNPLUS=(PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)+PR(9))
     >   /(LR(1)+LR(2)+LR(3)+LR(4)+LR(5)+LR(6))
      NPLUS=CNPLUS

      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,101)
 101   FORMAT(/2X,'N+',20X,'PRODUCTION',71X,':',8X,'LOSS RATES'/
     > ,4X,'ALT   [N+]   [N+]c     hv+N2   O++N2D  O+2P+N2',3X
     > ,'He++N2',3X,' hv+N   O2++N2D  N2++N4S O+(2D)+N4S  He++NO'
     > ,3X,'N++O2    N++O2    N++O2    N++O2    N++O2    N++O')
      IF(JPR.GT.0) WRITE(I,7) Z,NPLUS,CNPLUS
     > ,(PR(K),K=1,9),(LR(K)*NPLUS,K=1,6)
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CN2A(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE
     > ,N2A,P3X1,P3X2,P3X3,P3X4)
C........n2(a3sigma) and total LBH
      IMPLICIT REAL(A-H,L,N-Z)
      REAL P3X1,P3X2,P3X3,P3X4
      DIMENSION RTS(99),LR(22),PR(22)
C....... pr(1,2,3)= electron impact excitation of n2(a,b,c) states
      PR(1)=P3X1
      PR(2)=P3X2
      PR(3)=P3X3
      LR(1)=RTS(36)*ON
      LR(2)=RTS(27)*ON
      LR(3)=0.57
      N2A=(PR(1)+PR(2)+PR(3))/(LR(1)+LR(2)+LR(3))
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,102)
 102   FORMAT(/2X,'N2(A)',12X,'PRODUCTION',13X,':',5X,'LOSS RATES'
     > ,3X,':  Total LBH'
     > /,3X,'ALT',3X,'N2(A)',3X,'e*->N2A',3X,'e*->N2B',3X,'e*->N2C',2X
     >  ,'N2A>O1S',2X,'N2A>NO',2X,'RAD',5X,'LBH')
      IF(JPR.GT.0) WRITE(I,7) Z,N2A,(PR(K),K=1,3),(LR(K)*N2A,K=1,3)
     > ,P3X4
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE CN2P(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,P1,L1
     > ,N2P,P3X7,UVDISN,O2P,NNO,N2PLUS)
C....... N(2P). the rates are from Zipf et al JGR, 1980 p687
C.... 21-AUG-1992. Added N2+ recombination source
      IMPLICIT REAL(A-H,L,N-Z)
      DIMENSION RTS(99),LR(22),PR(22)
      PR(1)=P3X7
      PR(2)=RTS(64)*UVDISN
      PR(3)=RTS(73)*RTS(11)*N2PLUS*NE
      LR(1)=RTS(37)*ON
      LR(2)=RTS(38)*O2N
      LR(3)=RTS(39)*O2P
      LR(4)=RTS(40)*NNO
      LR(5)=RTS(57)
      LR(6)=RTS(58)
      LR(7)=(RTS(96)+RTS(97))*NE    !..Fox
      P1=PR(1)+PR(2)+PR(3)
      L1=LR(1)+LR(2)+LR(3)+LR(4)+LR(5)+LR(6)+LR(7)
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,103)
 103   FORMAT(/2X,'N(2P)',9X,'PRODUCTION',17X,':',20X,'LOSS RATES'/
     > ,3X,'ALT',3X,'[N2P]',3X,'e+N2',5X,'hv+N2',3X,'e+N2+',6X,'+O  '
     > ,3X,'+O2      +O2+      +NO       +2D     +4S      +e')
      IF(JPR.GT.0) WRITE(I,7) Z,N2P,(PR(K),K=1,3),(LR(K)*N2P,K=1,7)
      RETURN
 7    FORMAT(F6.1,1P,22E9.2)
      END
C:::::::::::::::::::::::::::::: CNOPV ::::::::::::::::::::::::::::::::::
C...... This routine calculates the vibrational distribution of no+
C...... Uses AFRL report by Winick et al. AFGL-TR-87-0334, Environmental
C...... Research papers, NO. 991, "An infrared spectral radiance code 
C...... for the auroral thermosphere (AARC)
C...... Written by P. Richards in February 2004
      SUBROUTINE CNOPV(JPR,I,JPT,Z,RTS,ON,O2N,N2N,NE,P1,NOP,OPLS
     >  ,N2PLS,O2P,N4S,NNO,NPLUS,N2P,PLYNOP,VCON,N2D,OP2D)
      IMPLICIT NONE
      INTEGER JPR,I,JPT,INV,IJ,IV,K
      PARAMETER (INV=20)            !.. NO+(v) array dimensions
      REAL Z,RTS(99),   !.. Altitude, rate coefficients
     >  ON,O2N,N2N,NE,              !.. O, N2, O2, electron densities
     >  P1,                         !.. total source output for finding [e] 
     >  NOP,OPLS,N2PLS,O2P,         !.. NO+, )+,N2+,O2+ densities
     >  N4S,NNO,NPLUS,N2P,          !.. N(4S), NO, N+, N(2P) densities
     >  PLYNOP,VCON,                !.. Lyman-a source, N2(v) rate factor
     >  N2D,OP2D,                   !.. N(2D), O+(2D) densities                
     >  NOPV(INV),NOPTOT,           !.. NO+(v) densities and total NO+ density
     >  LR(22),PR(22),              !.. storage for NO+ sources and sinks
     >  EINSCO1(INV),EINSCO2(INV),  !.. Einstein coeffs for delv=1,2
     >  LRV(INV),                   !.. NO+(v) + e rate factors
     >  PNOPV,LNOPV,                !.. Sources and sinks of NO+(v)
     >  PCASC,LRAD,                 !.. Temp total cascade source, sink
     >  K_N2_Q,P_N2_Q,L_N2_Q        !.. N2 queching rate :- coeff, source, sink

      !.. Fractions of each source going to each vib. level. Assume
      !.. N+ + O2 fractions for each source. NEED UPDATE
      REAL PRV1(INV),PRV2(INV),PRV3(INV),PRV4(INV),PRV5(INV),PRV6(INV),
     >  PRV7(INV),PRV8(INV),PRV9(INV),PRV10(INV),PRV11(INV),PRV12(INV)
      DATA PRV1/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV2/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV3/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV4/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV5/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV6/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV7/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV8/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV9/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV10/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/
      DATA PRV12/0,.05,.07,.09,.11,.13,.14,.17,.07,.01,.02,.06,.08,7*0/

      DATA K_N2_Q/7.0E-12/  !.. Quenching rate coeff. by N2
      DATA EINSCO1/0.0,10.9,20.2,28.4,35.5,41.5,46.6,50.9,54.3,57.0,
     >     58.9,60.2,60.8,60.7,59.9,5*60.0/  !.. Einstein coeff delv=1
      DATA EINSCO2/0.0,0.0,.697,1.93,3.61,5.74,8.24,11.1,14.2,17.7,
     >     21.3,25.1,29.0,33.2,37.4,5*40.0/ !.. Einstein coeff delv=1
      !.. rate factors for NO+(v)+e -> N + O. Sheehan and St-Maurice 2004
      DATA LRV/1.0,19*0.3333/    
      
      !... Evaluate total production and loss rates
      PR(1)=VCON*RTS(3)*N2N*OPLS        !.. N2 + O+
      PR(2)=N2PLS*ON*RTS(10)            !.. N2+ + O
      PR(3)=O2P*N4S*RTS(21)             !.. O2+ + N(4S)
      PR(4)=O2P*NNO*RTS(23)             !.. O2+ + NO
      !.. N+ + O2 -> O2+ + N(2D,4S) or NO+ + O(1S)
      PR(5)=(RTS(30)+RTS(66)+RTS(59))*NPLUS*O2N
      PR(6)=RTS(37)*N2P*ON              !.. N2+ + O
      PR(7)=RTS(24)*OPLS*NNO            !.. O+ + NO
      PR(8)=PLYNOP*NNO                  !.. Lyman-a + NO
      PR(9)=O2P*N2D*RTS(77)             !.. Fox: O2+ + N(2D)
      PR(10)=N2PLS*NNO*RTS(80)          !.. Fox: N2+ + NO
      PR(11)=NPLUS*NNO*RTS(81)          !.. Fox: N+ + NO
      PR(12)=RTS(83)*NNO*OP2D           !.. Fox: O+(2D) + NO
      PR(13)=OP2D*RTS(90)*N2N           !.. -> NO+ + N, Li et al. [1997] 
      LR(1)=NE*RTS(5)                   !.. NO+ + e

      !..Total source term used in main program to calculate [e]
      P1=PR(1)+PR(2)+PR(3)+PR(4)+PR(5)+PR(6)+PR(7)+PR(8)
     >    +PR(9)+PR(10)+PR(11)+PR(12)+PR(13)
      NOP=P1/LR(1)         !.. NO+ density

      DO IJ=1,INV
        NOPV(IJ)=0.0
      ENDDO
      NOPTOT=0.0

      !.. loop down evaluating the vibrational populations. Must start 
      !.. less than INV-1 because need cascade from v+2
      DO IV=INV-4,1,-1
        !... chemical production for v=IV = total source * fraction 
        PNOPV=PR(1)*PRV1(IV)+PR(2)*PRV2(IV)+PR(3)*PRV3(IV)+
     >    PR(4)*PRV4(IV)+PR(5)*PRV5(IV)+PR(6)*PRV6(IV)+
     >    PR(7)*PRV7(IV)+PR(8)*PRV8(IV)+PR(9)*PRV9(IV)+
     >    PR(10)*PRV10(IV)+PR(11)*PRV11(IV)+PR(12)*PRV12(IV)

        !.. cascade production from v+1, v+2
        PCASC=NOPV(IV+1)*EINSCO1(IV+1)+NOPV(IV+2)*EINSCO2(IV+2)
        LRAD=EINSCO1(IV)+EINSCO2(IV)   !.. total radiative loss

        L_N2_Q=K_N2_Q*N2N              !.. sink of quanta by N2 quenching
        IF(IV.EQ.1) L_N2_Q=0.0

        P_N2_Q=K_N2_Q*N2N*NOPV(IV+1)   !.. source of quanta by N2 quenching
        LNOPV=LR(1)*LRV(IV)            !.. recombination rate for level IV

        !.. evaluate NO+(iV) population
        NOPV(IV)=(PNOPV+PCASC+P_N2_Q)/(LNOPV+LRAD+L_N2_Q)
        NOPTOT=NOPTOT+NOPV(IV)  !.. total NO+ concentration

          !... diagnostic print. Set alt range to invoke
          IF(JPR.GT.0.AND.Z.GE.0.AND.Z.LT.10)
     >     WRITE(6,'(F10.1,I7,1P,22E10.2)') 
     >     Z,IV,PNOPV,P1,PCASC,P_N2_Q,LNOPV,LRAD,L_N2_Q,
     >     NOPV(IV),NOP,NOPTOT
      ENDDO

      PR(9)=PR(9)+PR(10)+PR(11)+PR(12)         !.. for printing only
      IF(JPT.EQ.1.AND.JPR.GT.0) WRITE(I,96)
 96   FORMAT(/5X,'NO+',34X,'PRODUCTION',69X,':LOSS RATE'/
     > ,3X,'ALT NO+(v=0) NO+(v=1) NO+(v=2)  NO+(v=3) O++N2    N2++O',
     >  4X,'O2++N4S   O2++NO   N++O2    N2P+O   O++NO   hv+NO',
     >  4X,'Other_P   NO++e')
      IF(JPR.GT.0) WRITE(I,'(F6.1,1P,22E9.2)')  Z,
     >   (NOPV(K),K=1,4),(PR(K),K=1,9),LR(1)*NOP

      RETURN
      END
C:::::::::::::::::::::::::::::::: TFILE :::::::::::::::::::::::::
C------- This file checks to see if a file exists for the FORTRAN unit
C------- JUNIT and returns 0 for no and 1 for yes
       SUBROUTINE TFILE(JUNIT,IOPEN)
       CHARACTER ACHAR
       IOPEN=1
       READ(JUNIT,90,END=70,ERR=70) ACHAR 
 90    FORMAT(A)
       REWIND JUNIT
       RETURN

 70    CONTINUE
       !--- File did not exist
       IOPEN=0 
       RETURN
       END
C
C
C.................... FLIPAP.FOR;2 ..........14-JUN-1994 21:36:29.18 
C....... This subroutine provides the 7 Ap indices for the MSIS model given
C....... the time history of the Kp at 3 hour intervals.
C....... Original programmer - D. A. Burns, June  1988
C....... UTHRS is the universal time at which Ap is to be evaluated (hours)
C....... RUNHRS is the length of the run (hours). Ap is the output array
C....... This routine was modified by P. Richards in July 1991 to input the
C....... 3 hr Kp indices instead of Ap and also F10.7. The Kp and F10.7 (Sa)
C....... indices can be found in the
C....... back of JGR and are read from a file coverted to Ap and stored in
C....... the array AP3HR. SW is an array of switches for the MSIS model
C....... If a negative Kp is read, the plasmaspheric H+ density (HPEQ) is
C....... reduced to simulate emptying of flux tubes.
C....... Modified July 1995 by Scot Braze to read Kp and F10.7 values from
C....... a master file.  STDAY is the start day in YYYYDDD format.  F107A 
C....... is the average F10.7 value.  It reflects the average of the 40
C....... days prior to the date and 40 days after the date.
C
      SUBROUTINE FINDAP (STDAY,UTHRS,RUNHRS,AP,AP3HR,SW,HPEQ,F107
     >                   ,F107A)
C
      INTEGER IND,INDSAV,NUMAP3,STDAY,I,DAYDIM
      PARAMETER (DAYDIM=801)
      REAL AP3HR(8001),AP(7),SW(25),HP3HR(8001),F107,F107A
     > ,T107(DAYDIM),T107A(DAYDIM),UTHRS
      REAL HPEQ,RUNHRS
      LOGICAL DEBUG
C
      DATA  UTST,INDSAV, DEBUG   ,    T107    ,   T107A    , THPEQ
     >   /   0.0,  1   , .FALSE. , DAYDIM*-1.0, DAYDIM*-1.0, 0.0/
C
C........ If this is the first call to FINDAP, call READAP  to read
C........ the 3 Hour Ap indices and check there is enough. HP3HR is
C........ used to reduce plasmaspheric content if negative
C
      IF (AP3HR(1).LT. 0.0) THEN
         CALL READAP(STDAY,UTST,AP3HR,NUMAP3,UTHRS,RUNHRS,HP3HR,T107
     >               ,T107A)
C....... call TSELEC and GSELEC to allow MSIS and HWM to use the 3 hour AP
         SW(9)= -1.0
         CALL TSELEC(SW) 
C
      ENDIF
C
C------ Set daily F10.7 flux
      F107 = T107(INT((UTHRS-UTST)/24)+1)
      F107A= T107A(INT((UTHRS-UTST)/24)+1)
C
C....  IND - index of the 3 hour AP for the current time - UTHRS
      IND = 20 + INT((UTHRS-UTST)/3)
C
C...... If the index has not changed do not recalculate APs
      IF (IND .EQ. INDSAV) THEN
         RETURN
      ELSE
         INDSAV = IND
      ENDIF

      !*** HPEQ is now adjusted in RSMNSD 19 July 2000
 
      IF (DEBUG) WRITE(6,*) 'START:',UTST,' ','NUMAP3 = ',NUMAP3
C
C..... Calculate the daily Ap (AP(1)) by first determining the day which
C..... corresponds to the current UTHRS, then calculate the index that
C..... corresponds to the first 3 hour Ap of that day. Then sum 8 3 hour
C..... APs for that day
      DAY = INT(UTHRS/24)
      IDAY = 20 + NINT((DAY * 24 - UTST)/3)
      AP(1)=0.0
      DO 25 I = IDAY, (IDAY+7)
         AP(1) = AP(1)+AP3HR(I)
25    CONTINUE
      AP(1)=AP(1)/8.0
C
C..... Fill the next 4 elements of AP with the corresponding 3 hour values
      DO 20 I = 2, 5
        AP(I) = AP3HR(IND-I+2)
        IF (DEBUG) WRITE (6,*)'I=',I,' ','IND=',IND,' ','AP3HR=',
     >   AP3HR(IND-I+2),'CT=',UTHRS
20    CONTINUE
C
C...... AP(6) is the average of eight 3 hour indices from 12 to 33 hours
C...... prior to current time
      AP(6) = 0.0
      DO 30 I = 4, 11
        AP(6) = AP(6) + AP3HR(IND-I)
        IF (DEBUG) WRITE(6,*)'I=',I,' ','SUM6=',AP(6),'AP3HR=',
     >     AP3HR(IND-I),'CT=',UTHRS
30    CONTINUE
      AP(6) = AP(6)/8.0
C
C...... AP(7) is the average of eight 3 hour indices from 36 to 60 hours
C...... prior to current time
      AP(7) = 0.0
      DO 40 I = 12, 19
        AP(7) = AP(7) + AP3HR(IND-I)
        IF (DEBUG) WRITE(6,*)'I=',I,' ','SUM7=',AP(7),'AP3HR=',
     >     AP3HR(IND-I),'CT=',UTHRS
40    CONTINUE
      AP(7) = AP(7)/8.0
      RETURN
      END
C:::::::::::::::::::::::::::::::::: READAP ::::::::::::::::::::::::::
C..... This subroutine reads in the Start time for the run (UTST) and the
C..... 3 hour Kp indices converts them to Ap and returns them in (AP3HR).
C..... It also returns the number of 3 hour indices (NUMAP3). and tests
C..... the data to see if there is enough
C..... and if it within the range 0-300. UTHRS is the first time that the
C..... Kp is required. It is tested to see if it is within an hour of UTST
C..... RUNHRS is the length of the run. All times are in hours.  Modified
C..... 8/7/95 by Scot A Braze.  STDAY is the start day in YYYYDDD format.
C..... FYYYY AND FDDD are the start year and day num (out of 365) of the 
C..... run.  SYYYY AND SDDD are the day and year that the data extraction
C..... begins.  CYYYY AND CDDD are the current day and year being read.  
C..... IKPAP is the integer array used to hold kp values to be converted 
C..... to real. T107A is the average F10.7 value.  The f10.7 values are 
C..... returned in T107, and the Ap values are returned in AP3HR.
C
      SUBROUTINE READAP (STDAY,UTST,AP3HR,NUMAP3,UTHRS,RUNHRS
     >                   ,HP3HR,T107,T107A)
      IMPLICIT NONE
C
      INTEGER STDAY,SYYYY,SDDD,CDDD,CMONTH,CDAY,FYYYY,FDDD
     >        ,IKPAP(8),NDAY,I,K,NUMAP3,IDD,IOPEN,CYYYY,DAYDIM
      PARAMETER (DAYDIM=801)
      REAL UTST,AP3HR(8001),KPTOAP(0:90),HP3HR(8001)
     >         ,T107(DAYDIM),T107A(DAYDIM),UTHRS,SENT
      REAL RUNHRS
      LOGICAL DEBUG
C......Maximum number of AP indices allowed for a FLIP run
      DATA DEBUG / .FALSE. /
C....... Conversion factors from Kp = 1..9. AP = KPTOAP(KP) - obsolete
      !..     Kp= 0    1    2   3    4    5    6     7     8    9
      !..     AP= 0,   3,   7,  15,  27,  48,  80,  140,  240, 400
      !.. 90 Ap values for easy conversion to Ap
      DATA KPTOAP/3*0,4*2,3*3,3*4,4*5,3*6,3*7,4*9,3*12,3*15,4*18,3*22
     >   ,3*27,4*32,3*39,3*49,4*56,3*67,3*80,4*94,3*111,3*132,4*154
     >   ,3*179,3*207,4*236,3*300,400/
C
      IF (DEBUG) WRITE (6,*)'*******ENTERING READAP********'
C------- Test to see if the data file exists
      CALL TFILE(20,IOPEN)
      IF(IOPEN.EQ.0) THEN
        WRITE(6,79) 
 79     FORMAT(/1X,'*** File with 3 hour Ap and F10.7 is missing ***'/)
        CALL RUN_ERROR    !.. print ERROR warning in output files
        STOP
      ENDIF
C
C.... Set the number of days for the run. Add a day to be sure
      NDAY = NINT((UTHRS+RUNHRS)/24.0)+1
      IF(NDAY.GT.801) THEN
        WRITE(6,*) ' '
        WRITE(6,*) ' ** RUN is too long must be <= one YEAR **'
        CALL RUN_ERROR    !.. print ERROR warning in output files
        STOP
      ENDIF 
C
C---- Get the day the FLIP run begins.  FYYYY and FDDD are
C---- the flip starting year and day for the run.  
      FYYYY=STDAY/1000
      FDDD=MOD(STDAY,1000)
C---- Check to see if 3 days prior to run is in the previous year.
      IF(FDDD.LT.4) THEN
          IF(MOD(FYYYY-1,4).EQ.0) THEN
              SDDD=366-(3-FDDD)
              SYYYY=FYYYY-1
          ELSE
              SDDD=365-(3-FDDD)
              SYYYY=FYYYY-1
          ENDIF
      ELSE
          SDDD=FDDD-3
          SYYYY=FYYYY
      ENDIF
      IF(DEBUG) WRITE(6,*) 'Start date for Kp values is',SYYYY,SDDD
C
C.... First discard the header lines.
  30  CONTINUE
      READ(20,444,ERR=30) SENT
      IF(DEBUG) WRITE(6,*) 'SENT = ',SENT
  444 FORMAT(F4.1)
C
C**************************** MAIN LOOP *****************************
C---- Read F10.7 indices for up to DAYDIM days. T107 & T107A are padded with
C---- negative values.  Loop through until 3 days prior to the start of 
C---- the run.  The Kp values for these 3 days must be extracted as well 
C---- as the F10.7 and Kp values for the length of the run.
      DO 10 I=1,999999
         READ(20,*,END=999,ERR=999) CYYYY,CMONTH,CDAY,(IKPAP(K)
     >                             ,K=1,8),T107(1),T107A(1)
         CALL CONV_DATE(CDDD,CYYYY,CMONTH,CDAY)
         IF(SDDD.EQ.CDDD .AND. SYYYY.EQ.CYYYY) THEN
              CALL GET_DATA(CYYYY,CDDD,NDAY,IKPAP,HP3HR,T107,T107A)
              GOTO 50
         ENDIF
   10 CONTINUE
C************************** end main loop. ********************
C
  50  CONTINUE
C....... Test F107 for bad data.
      DO 125 IDD=1,NDAY
        IF(T107(IDD).LT.50.0.OR.T107(IDD).GT.400.OR.
     >    T107A(IDD).LT.50.0.OR.T107A(IDD).GT.400) THEN
          WRITE(6,96) 
 96       FORMAT(/'  ERROR!, Invalid F10.7 or F107A value'
     >  ,1X,'in F10_Kp data file'/)
          CALL RUN_ERROR    !.. print ERROR warning in output files
          STOP
        ENDIF
 125  CONTINUE
C
C----- Check the Kp for bad data
 490  DO  25 I = 1, 8*(NDAY+2)+3
         AP3HR(I)= ABS(HP3HR(I))
         NUMAP3 = NUMAP3 + 1
C.....   Kp was read from file: check magnitude and convert to Ap
         IF(AP3HR(I).GT.9) THEN
            WRITE(6,*) ' **** Kp index in file must be 0< Kp <=9  ****'
            CALL RUN_ERROR    !.. print ERROR warning in output files
            STOP
         ELSE 
            AP3HR(I) = KPTOAP(NINT(AP3HR(I)*10))  !.. look up Ap
         ENDIF
         !..  WRITE (16,*) AP3HR(I),' ','AP INDEX',I
25    CONTINUE
      RETURN
  999 WRITE(6,*) '*** ERROR -- Start date not found in Kp data file.'
      WRITE(6,*) '*** Check the F10_KP input file in run file.'

      CALL RUN_ERROR    !.. print ERROR warning in output files
      STOP
      END
C************************** SUBROUTINE CONV_DATE ***********************
C---- Scot A Braze,  8/7/95
C---- This subroutine converts the date from YYYY MM DD to YYYY DDD. 
C
      SUBROUTINE CONV_DATE(DDD,YYYY,MM,DD)
      IMPLICIT NONE
      INTEGER DDD,MM,DD,NCONV(12),LYCONV(12),YYYY
      LOGICAL DEBUG
      DATA DEBUG /.FALSE./
C
      DATA NCONV/0,31,59,90,120,151,181,212,243,273,304,334/
      DATA LYCONV/0,31,60,91,121,152,182,213,244,274,305,335/
C
      IF(MOD(YYYY,4).EQ.0) THEN
          DDD=LYCONV(MM)+DD
      ELSE
          DDD=NCONV(MM)+DD
      ENDIF
      IF(DEBUG) WRITE(6,*) YYYY,DDD
      END
C*************************** SUBROUTINE GET_DATA ************************
C---- Scot A Braze,   8/7/95
C---- This subroutine gets the kp values from the data file.  It gets the 
C---- 19 values prior to 0.0 UT.  It then gets the kp and F10.7 values for 
C---- the length of the run.
C
      SUBROUTINE GET_DATA(PYYYY,PDDD,NDAY,IKPAP,HP3HR,T107,T107A)
      IMPLICIT NONE
      INTEGER IKPAP(8),I,J,K,L,NDAY,CDDD,CYYYY,PDDD,PYYYY,TDAY,TMONTH
     > ,DAYDIM
      PARAMETER (DAYDIM=801)
      REAL HP3HR(8001),T107(DAYDIM),T107A(DAYDIM)
      LOGICAL LY
      DATA J,L /2*1/
C
C---- first get the 3 values from the third day before start day.
      DO 300 I=6,8
         HP3HR(J)=REAL(IKPAP(I))/10
         J=J+1
  300 CONTINUE
C---- now loop through for NDAY + 2 days to get kp values prior to and
C---- after start day and the F10.7 value for the length of the run.
      DO 200 I=1,(NDAY+2)
          READ(20,*,END=500,ERR=500) CYYYY,TMONTH,TDAY,(IKPAP(K),K=1,8)
     >              ,T107(L),T107A(L)
          CALL CONV_DATE(CDDD,CYYYY,TMONTH,TDAY)
C---- Check to see if prev year is leap year or not.
      IF(MOD(PYYYY,4).EQ.0) THEN
          LY=.TRUE.
      ELSE
          LY=.FALSE.
      ENDIF
C---- Now check to make sure dates are contiguous. 
          IF(CYYYY.EQ.PYYYY) THEN 
             IF(PDDD.EQ.CDDD-1) THEN
                GOTO 310
             ELSE
                GOTO 510
             ENDIF
          ELSE
             IF(PYYYY+1.EQ.CYYYY) THEN
                IF(LY .EQV. .TRUE.) THEN
                   IF(CDDD.EQ.1 .AND. PDDD.EQ.366) THEN
                      GOTO 310
                   ELSE
                      GOTO 510
                   ENDIF
                 ELSE
                   IF(CDDD.EQ.1 .AND. PDDD.EQ.365) THEN
                      GOTO 310
                   ELSE 
                      GOTO 510
                   ENDIF
                 ENDIF            
             ELSE
                 GOTO 510
             ENDIF
          ENDIF
  310     DO 210 K=1,8
             HP3HR(J)=REAL(IKPAP(K))/10
             J=J+1
  210     CONTINUE
          IF(I.GT.2) L=L+1
          PYYYY=CYYYY
          PDDD=CDDD
  200 CONTINUE
      CLOSE(20)
      RETURN
  500 WRITE(6,*) '******* Not enough Kp values for the length of the ',
     >   'run.'
      CALL RUN_ERROR    !.. print ERROR warning in output files
      STOP
  510 WRITE(6,*) '****** Error, not enough days in the data Kp file',
     >  ' for the run.'
      CALL RUN_ERROR    !.. print ERROR warning in output files
      STOP
      END
C
C
C.................................... RATES.FOR ................. 
C.... This is the reaction rate subroutine for the FLIP model. It takes
C.... temperatures as input and puts the rates in array RTS. It includes
C.... reaction rates, efficiencies for various products, and Einstein
C.... coefficients. For a complete set of references see Fox and Sung JGR
C.... 2001, page 21,305. Rates different from Fox and Sung indicated by PGR
      SUBROUTINE RATS(J,TE,TI,TN,RTS)
      IMPLICIT REAL(A-H,L,N-Z)
      REAL TE,TI,TN,RTS,T13,TOT_NP_O2_RATE
      DIMENSION RTS(99)

      !.. zero out array
      DO 898 ITJS=1,99
 898  RTS(ITJS)=0.0

      !.. O + H+ -> O+ + H      Fox and Sung [2001]
      ZED=1+0.6*EXP(-228.0/TN)+0.2*EXP(-326.0/TN)
      RTS(1)=(8*6.4E-10/(9*ZED))
     >     *(EXP(-232.1/TI)+0.6*EXP(-228.0/TI)+0.2*EXP(-326.0/TI))

      !.. O+ + H -> O + H+    Anicich et al. [1993]
      RTS(2)=6.4E-10

      !.. O+ + N2 --> NO+ + N,   Hierl et al.[1997] 
      !.. The Hierl et al. [1997] lab rate is contaminated by N2(v) 
      !.. for T > 1300K. Therefore, the Hierl et al. rate is not really 
      !.. appropriate  in the ionosphere. The IDC model uses the Hierl et  
      !.. al. rate because it does not solve for N2(v). The FLIP model 
      !.. solves for N2(v) and uses the St. Maurice and Torr rate (JGR,1978,p969)
      IF(TI.LE.1000) RTS(3)=1.2E-12*(300/TI)**0.45     !.. Hierl et al.[1997] 
      IF(TI.GT.1000) RTS(3)=7.0E-13*(TI/1000)**2.12    !.. Hierl et al.[1997] 

      !.. O+ + O2 -> O2+ + O,   Lindinger et al. [1974] 
      !.. Hierl et al. lists different rates. Hierl et al. [1997] not 
      !.. used above 1600 because rates are contaminated by O2(v) for 
      !.. T > 1000K. We don't know the vibrational state in the 
      !.. thermosphere. This fit was done by PGR May 2009. It is similar 
      !.. to Fox and Sung but does not increase sharply above 1000K.
      IF(TI.LE.1600) RTS(4)=1.6E-11*(300/TI)**0.52
      IF(TI.GT.1600) RTS(4)=6.7E-12*(TI/1600)**0.6 

      !.. NO+ + e -> N + O    Walls and Dunn [1974)
      !.. Vejby-Christensen et al [1998] gives 4.0E-7*(300/TE)**0.5
      !.. Torr and Torr [1979] gives 4.3E-7*(300/TE)**0.83(-0.16,+.08)
      !.. Sheehan and St. Maurice gives 3.5E-7*(300/TE)**0.65
      RTS(5)=4.0E-7*(300/TE)**0.85

      !.. O2+ + e -> O + O   Mehr and Biondi (1969)
      IF(TE.LE.1200) RTS(6)=1.953E-7*(300/TE)**0.70
      IF(TE.GT.1200) RTS(6)=7.389E-8*(1200/TE)**0.56

      !..  O2 + N(4S)-> NO + O           Baulch et al.[1994]
      RTS(7)=1.5E-14*TN*EXP(-3270.0/TN)

      !..   N(2D) + e -> N(4S) + e     Berrington and Burke [1981]
      RTS(8)=3.86E-10*(TE/300.)**0.81

      !..   NO + N(4S) -> N2 + O      Lee et al. [1978]
      RTS(9)=3.4E-11 

      !.. N2+ + O -> NO+ + N   Scott et al.[1999]
      IF(TI.LE.1500) RTS(10)= 1.33E-10*(300/TI)**0.44
      IF(TI.GT.1500) RTS(10)= 6.55E-11*(1500/TI)**(-0.2)

      !.. N2+ + e -> N + N  Mehr and Biondi (1969)
      RTS(11)=2.2E-7*(300/TE)**0.39    !.. Zipf (1980)

      !.. O+(2D) + e -> O+(4S) + e   McLaughlin and Bell (1998)
      !.. Henry [1969] gives 7.8E-8*(300/TE)**0.5
      RTS(12)=6.03E-8*(300/TE)**0.5

      !.. O+(2P) + e ->  O+(2D) + e   McLaughlin and Bell (1998)
      !.. RTS(13)+RTS(14) agrees with Walker et al (1975) and 
      !.. Chang et al (1993)
      RTS(13)=1.84E-7*(300/TE)**0.5

      !.. O+(2P) + e -> O+(4S) + e  McLaughlin and Bell (1998)
      RTS(14)=3.03E-8*(300/TE)**0.5

      !.. N(2D) + O ->  N(4S) + O  Fell et al.[1990]. Lin and Kaufman[1971]
      RTS(15)=6.9E-13

      !.. N(2D) + O2 -> NO + O  Herron[1999]. Shihira et al.[1994]
      RTS(16)=9.7E-12*EXP(-185.0/TN)

      !.. N2+ + O2 -> O2+ + N2   Scott et al.[1999]
      IF(TI.LT.1000) THEN
        RTS(17)=5.1E-11*(300/TI)**1.16
      ELSEIF(TI.LE.2000) THEN
        RTS(17)=1.26E-11*(TI/1000)**0.67
      ELSE
        RTS(17)=2.39E-11
      ENDIF

      !.. thermal electron excitation of O(1D); Rees et al 1967 pss, p1097 .....
      RTS(18)=1.1E-10*SQRT(TE)*EXP(-2.27E+4/TE)*(0.406
     >  +0.357E-4*TE-(0.333+0.183E-4*TE)*EXP(-1.37E4/TE)
     >  -(0.456+0.174E-4*TE)*EXP(-2.97E4/TE))

      !.. N2 + O+(2D) -> N2+ + O   
      !..RTS(19)=8.0E-10                   !.. Johnson and Biondi
      RTS(19)=1.50E-10*(300/Ti)**(-0.55)   !.. Li et al by PGR
      
      !.. N2 + O+(2P) -> N2+ + 0    Fox 
      !.. RTS(20)=6.2E-10*EXP(-340/TI)   !.. Li et al from Fox wrong
      RTS(20)=2.0E-10*(300/Ti)**(-0.55)    !.. Li et al by PGR

      !.. O2+ + N(4S) -> NO+ + 0   Scott et al.[1999]
      RTS(21)=1.0E-10

      !.. N+ + O2 -> O+ + NO 
      !.. Torr and Torr gives 6.0E-10 for total N+ + O2 reaction rate
      !.. Dotan et al [1997] from Fox and Sung gives
      !IF(TI.LE.1000) TOT_NP_O2_RATE=2.02E-10*(300/TI)**(-0.45)
      !IF(TI.GT.1000) TOT_NP_O2_RATE=3.49E-10
      !.. does not seem to be correct. Probably vibrationally excited O2
      !.. Branching ratios for N+ + O2 from O'Keefe et al J. Chem. Phys. 1986
      !.. NO+ +O(3P) = .09, NO+ + O(1D) = .36, O2+ + N(4S) = 0.35, 
      !.. O2+ + N(2D) = 0.15, O+(4S) + NO = .05
      TOT_NP_O2_RATE=6.0E-10                !.. Total N+ + O2 rate
      RTS(22)=0.05*TOT_NP_O2_RATE      

      !.. O2+ + NO -> NO+ + O2 Midey and Viggiano [1999]
      RTS(23)=4.5E-10 * 1.0000

      !.. O+ + NO -> O + NO+   Dotan and Viggiano [1999]
      IF(TI.LE.300) RTS(24)=7.0E-13*(300/TI)**0.66
      IF(TI.GT.300) RTS(24)=7.0E-13*(TI/300)**0.87

      !.. N+ + O2 -> O2+ + N(4S) 
      RTS(25)=0.35*TOT_NP_O2_RATE 

      !.. O+(2P) + O -> O+(4S) + O 
      !..RTS(26)=5.2E-10  !.. Fox appears to be wrong  
      !.. (Chang et al., JGR 1993) c.f. 5.2E-11  (Rusch)    
      RTS(26)=4.0E-10

      !.. N2(A3sig) + O -> NO + N(2D) 
      RTS(27)=2.0E-11       !..see Campbell et al. 2006
      RTS(27)=0.000000      !.. Torr and Torr value

      !.. O+(2D) + O ->  O+(4S) + O  Torr and Torr [1980]
      RTS(28)=1.0E-11

      !.. O+ + N(2D) -> O + N+  Constantinides et al.[1979].Bates[1989]
      RTS(29)=1.3E-10

      !.. O2 + N+ -> O(3P) + NO+
      !.. Branching ratio from O'Keefe et al J. Chem. Phys. 1968
      RTS(30)=0.09*TOT_NP_O2_RATE 

      !.. O + N+ -> O+ + N   Constantinides et al.[1979].Bates[1989]
      RTS(31)=2.2E-12

      !.. Efficiency for   N2+ + e -> N(2D) + N(2D)
      RTS(32)=1.46

      !.. N2 + O(1D) -> O + NO
      RTS(33)=1.8E-11*EXP(107.0/TN)

      !.. O2 + O(1D) -> O + O2
      RTS(34)=3.2E-11*EXP(67/TN)

      !.. O2 + N(4S) -> O(1S) + NO. Kopp et al. 1977, JGR, p4715
      RTS(35)=2.5E-11


      !.. N2(A3sig) + O -> O(1S) + N2
      RTS(36)=2.5E-11*EXP(TN/298)**0.55    !..  see Campbell et al. 2006
      RTS(36)=2.0E-11                      ! .. Torr et al.

      !.. N(2P) + O -> products (N(2D,4S) and NO+) and O(3P,1D) 
      !.. from Piper et al 1993, J. Chem. Phys. vol 98 page 8560.
      RTS(37)=1.7E-11

      !.. N(2P) + O2 -> NO + O 
      RTS(38)=3.9E-12*EXP(-60/TN)

      !.. N(2P) quenching rates(O2+,NO) from Zipf et al jgr 1980 p687
      RTS(39)=2.2E-11
      RTS(40)=1.8E-10

      !.. N(2D) + NO -> N2 + O 
      RTS(41)=6.7E-11

      !.. efficiency N2+ + O -> N2 + O+(4S)   
      IF(TI.LE.1500) RTS(42)= 7.0E-12*(300/TI)**0.21
      IF(TI.GT.1500) RTS(42)= 4.83E-12*(1500/TI)**(-0.41)
      RTS(42)=RTS(42)/RTS(10)    !.. converts to efficiency

      !.. O+(2D) + O2 -> O2+ + O   Fox
      RTS(43)=7.0E-10

      !.. He+ + N2 -> He + N2+
      RTS(44)=5.2E-10

      !.. He+ + N2 -> He + N+
      RTS(45)=7.8E-10

      !.. O(1S)+ e -> O(1D) + e  
      RTS(46)=8.5E-9

      !.. O(1S)+ e -> O(3P) + e  
      RTS(47)=1.56E-10*(TE/300)**0.94

      !.. O(1S) + O2 -> O2 + O 
      RTS(48)=4.4E-12*EXP(-815.0/TN)

      !.. NO+ + e -> N(4S) + O
      RTS(49)=0.15 * RTS(5)

      !.. NO+ + e -> N(2D) + O
      RTS(50)=0.85 * RTS(5)

      !.. O2+ + e -> O(1D) + O
      RTS(51)=1.11 * RTS(6)

      !.. O2+ + e -> O(1S) + O
      RTS(52)=0.05 * RTS(6)

      !.. Efficiency for   N2+ + e -> N(4S) + N(2D)
      RTS(53)=0.46

      !.. O(1D) -> O + 6300 + 6364 
      RTS(54)=0.00934

      !.. O(1S) -> O(1D) + 5577
      RTS(55)= 1.06

      !.. O(1S) -> O(3P) + hv (2972) RTS(56)= 4.5E-2 !.. old value
      RTS(56)= 0.10 * RTS(55)  !.. From Slanger, Spring AGU 2005

      !.. N(2P) -> N(2D) + hv
      RTS(57)=7.9E-2

      !.. N(2P) -> N(4S) + hv
      RTS(58)=5.0E-3

      !.. N+ + O2 -> NO+ + O(1S) Langford et al., PSS, 33,1225,1985
      RTS(59)=1.0E-3*TOT_NP_O2_RATE 

      !.. Efficiency for   N2(A3sig) + O -> O(1S) + N2
      RTS(60)=0.37

      !.. N(2D) -> N(4S) + hv
      RTS(61)=1.07E-5

      !.. hv(>600A) + N2 -> N(4S) + N   branching ratio
      RTS(62)=0.5

      !.. hv(>600A) + N2 -> N(2D) + N   branching ratio
      RTS(63)=0.4

      !.. hv(>600A) + N2 -> N(2P) + N   branching ratio
      RTS(64)=0.1

      !.. N+ + O2 -> O2+ + N(2D)
      !.. Branching ratio from O'Keefe et al J. Chem. Phys. 1968
      RTS(65)=0.15*TOT_NP_O2_RATE 

      !.. N+ + O2 -> NO+ + O(1D)
      !.. Branching ratio from O'Keefe et al J. Chem. Phys. 1968
      RTS(66)=0.36*TOT_NP_O2_RATE 

      !.. hv(Scum-Runge) + O2 -> O(1S) + O   branching ratio
      RTS(67)=0.001

      !.. Effic of O2(A3,DEL) + O -> O(1S)
      RTS(68)=0.1

      !.. O(1D) + O -> O + O   Abreu et al. PSS, p1143, 1986
      RTS(69)=6.47E-12*(TN/300)**0.14

      !.. hv + N2 -> N+(5S) -> 2143 A emission yield from the 2s sigma g state  
      !.. of N2. This was taken as 0.6 the value of Cleary and Barth JGR 1987, 
      !.. p13,635 because they did not double EUV below 250 A.
      RTS(70)=0.06

      !.. hv + N2 -> N+(1D) -> 6584 A emission (guess)
      RTS(71)=0.3

      !.. hv + N2 -> N+(1S) -> 5755 A emission (guess)
      RTS(72)=0.03

      !.. efficiency of production of N(2P) from e + N2+ reaction
      RTS(73)=0.08

      !.. Efficiency for production of O(1D) from N(2D) + O2 reaction
      !.. See Link and Swaminathan, PSS, 1992, page 699
      RTS(74)=0.1    !??? check

      !.. He+ + O2 -> He + O2+
      RTS(75) = 9.2E-12

      !.. He+ + O2 -> He + O+(2D) + O(3P) 
      RTS(76) = 2.37E-10

      !.. O2+ + N(2D) -> NO+ + O
      RTS(77) = 1.8E-10

      !.. O2+ + N(2D) -> N+ + O2
      RTS(78) = 8.65E-10

      !.. N2+ + N(4S) -> N+ + N2
      RTS(79) = 1.0E-11

      !.. N2+ + NO -> NO+ + N2
      RTS(80) = 3.6E-10

      !.. N+ + NO -> N(4S) + NO+
      RTS(81) = 4.72E-10*(300/TI)**0.24

      !.. N+ + NO -> N2+ + O
      RTS(82) = 8.33E-11*(300/TI)**0.24

      !.. O+(2D) + NO -> NO+ + O
      RTS(83)=1.2E-9

      !.. O+(2D) + N -> N+ + O
      RTS(84)=1.5E-10

      !.. O+(2P) + O2 -> O+ + O2  Fox
      RTS(85)=1.3E-10

      !.. O+(2P) + O2 -> O2+ + O
      RTS(86)=1.3E-10

      !.. O+(2P) + N -> O+ + N(2D)
      RTS(87)=1.0E-11

      !.. O+(2P) + NO -> NO+ + O
      RTS(88)=1.2E-9

      !.. H+ + O2 -> O2+ + H
      RTS(89)=3.8E-9
 
      !.. O+(2D) + N2 -> NO+ + N  !.. Li et al. (1997).
      !.. From the ratio of the cross sections.
      !.. The branching ratio to O+(4S) + N2 not given by Li et al.
      RTS(90)=2.5E-11

      !.. He+ + O2 -> He + O+(4S) + O 
      RTS(91) = 2.39E-11

      !.. He+ + O2 -> He + O+(2P) + O 
      RTS(92) = 6.04E-10

      !.. He+ + O2 -> He + O+(4S) + O(1D)
      RTS(93) = 4.6E-11

      !.. He+ + NO -> He + N+ + O
      RTS(94) = 1.35E-9

      !.. He+ + NO -> He + O+ + N
      RTS(95) = 1.0E-10

      !.. N(2P) + e -> N(4S) + e
      RTS(96)=2.04E-10*(TE/300)**0.85
 
      !.. N(2P) + e -> N(2D) + e
      RTS(97)=9.5E-9

      !.. O(1D) + e -> O(3P) + e
      RTS(98)=2.87E-10*(TE/300)**0.91

      !.. N2+ + O -> O+ + N2  !.. McFarland et al.(1974)
      !.. From Fox and Sung 2001
      RTS(99)=0.07*1.0E-10*(300/Ti)**0.23

        RETURN
        END
C:::::::::::::::::::::::::::::::::::: RATCHK :::::::::::::::::::::::::::::
C.. this subroutine checks the reaction rates from subroutine rats
C.. against a standard set and prints a warning if any are different
C.. Modified in April 20008 to write warnings in multiple files
      SUBROUTINE RATCHK(NUMU,  !.. number of files to write rate message
     >               UNITNUM)  !.. Unit numbers to write message
      REAL RTS(99),RATIO,TSTAND
      INTEGER K              !.. loop control
      INTEGER NUMU           !.. number of units to write message
      INTEGER UNITNUM(22)    !.. Unit numbers for writing warning
      INTEGER IRTS(99)       !.. # of rates changed    
      REAL R(99)             !.. standard reaction rate values
      DATA RTS/99*0.0/
      !.. rate values at the standard temperature
      DATA R/4.96E-10,6.40E-10,6.7E-13,8.56E-12,1.44E-07,8.41E-08
     > ,5.68E-13,1.02E-09,3.40E-11,7.83E-11,1.13E-07,3.30E-08,1.01E-07
     > ,1.66E-08,6.90E-13,8.06E-12,1.26E-11,2.08E-19,2.91E-10,3.88E-10
     > ,1.00E-10,0.0E-10,4.5E-10,1.99E-12,3.47E-10,4.0E-10,0.0,1.0E-11
     > ,1.30E-10,7.42E-11,2.20E-12,1.46E+00,2.00E-11,3.42E-11,2.50E-11
     > ,2.00E-11,1.70E-11,3.67E-12,2.20E-11,1.80E-10,6.70E-11,6.94E-02
     > ,7.00E-10,5.20E-10,7.80E-10,8.50E-09,4.83E-10,1.95E-12,2.16E-08
     > ,1.22E-07,9.34E-08,4.21E-09,4.60E-01,9.34E-03,1.06E+00,1.06E-01
     > ,7.90E-02,5.00E-03,6.00E-13,3.70E-01,1.07E-05,5.00E-01,4.00E-01
     > ,1.00E-01,1.49E-10,3.01E-10,1.00E-03,1.00E-01,7.66E-12,6.00E-02
     > ,3.00E-01,3.00E-02,8.00E-02,1.00E-01,9.20E-12,2.37E-10,1.80E-10
     > ,8.65E-10,1.00E-11,3.60E-10,3.54E-10,6.24E-11,1.20E-09,1.50E-10
     > ,1.30E-10,1.30E-10,1.00E-11,1.20E-09,3.80E-09,2.50E-11,2.39E-11
     > ,6.04E-10,4.60E-11,1.35E-09,1.00E-10,5.67E-10,9.50E-09,8.58E-10
     > ,5.31E-12/


      JRTS=0
      !.. call RATS with standard temperature TSTAND = 999
      TSTAND = 999.0
      CALL RATS(1,TSTAND,TSTAND,TSTAND,RTS)
      DO 20 I=1,99
      IF(R(I).GT.0) RATIO=RTS(I)/R(I)
      IF(R(I).LE.0.AND.RTS(I).EQ.0) RATIO=1.0
      IF(R(I).LE.0.AND.RTS(I).NE.0) RATIO=2.0
      IF(RATIO.GT.1.01.OR.RATIO.LT.0.99) THEN
        JRTS=JRTS+1
        IRTS(JRTS)=I
	ENDIF
 20   CONTINUE

      !.. Write warning in files
      IF(JRTS.GT.0) THEN
        DO K=1,NUMU
          WRITE(UNITNUM(K),88) (IRTS(I),I=1,JRTS)
        ENDDO
        DO K=1,NUMU
          WRITE(UNITNUM(K),89) (R(IRTS(I)),I=1,JRTS)
        ENDDO
        DO K=1,NUMU
          WRITE(UNITNUM(K),90) (RTS(IRTS(I)),I=1,JRTS)
        ENDDO
        DO K=1,NUMU
          WRITE(UNITNUM(K),*) ' '  !.. add a blank line
        ENDDO
      ENDIF
 88   FORMAT(2X,'*** WARNING: Non-standard reaction rates'
     >  ,1X,'in FLIP, #s:',9I9)
 89   FORMAT(2X,'*** The FLIP standard reaction rates at'
     > ,1X,'Te=Ti=Tn=999 K:',1P,9E9.2)
 90   FORMAT(2X,'*** The  non-standard reaction rates at'
     > ,1X,'Te=Ti=Tn=999 K:',1P,9E9.2)
      RETURN
      END
C
C
C.........................<PESIMP.FOR>......................3 APR 92
C...... This test driver demonstrates how to call the model and 
C...... how to calculate electron heating rate and 3371 excitation rate.
      SUBROUTINE SECIPRD(ALT,SZADEG,F107,F107A,
     >    TE,TN,OXN,O2N,N2N,XNE,N2APRD)
      INTEGER I,K,IK           !-- loop control variables
      INTEGER IDIM             !.. Array dimensions
      INTEGER IMAX             !.. Maximum PE energy
      PARAMETER (IDIM=501)
      REAL PEFLUX(IDIM)        !-- PE flux
      REAL SIGIT(3)            !-- Total electron impact cross sections
      REAL SIGEX(22)           !-- Electron impact cross sections for OX
      REAL ALT                 !-- ALT = altitude (km)  { 120 -> 500 }
      REAL SZADEG              !-- solar zenith angle {0 -> 90 degrees}
      REAL F107, F107A         !-- F107 = Solar 10.7 cm flux
      REAL TE,TN               !-- electron, neutral temperatures (K)
      REAL XN(3),OXN,O2N,N2N   !-- XN, O, O2, N2, neutral densities  (cm-3)
      REAL XNE                 !-- electron density  (cm-3)
      REAL XN2D                !-- N(2D) density for N(2D) + e -> 2.5 eV
      REAL XOP2D               !-- O+(2D) density for O+(2D) + e -> 3.3 eV
      REAL SPRD(3,6)
      REAL SIGOX,SIGN2,SIGEE  !.. Total exciation cross sections for O, N2, O2
      REAL N2APRD             !.. Production of N2A
      REAL DE(IDIM),EV(IDIM)
	!.. various ionization and excitation rates by EUV and PE
      REAL EUVION,PEXCIT,PEPION,OTHPR1,OTHPR2
      COMMON/EUVPRD/EUVION(3,12),PEXCIT(3,12),PEPION(3,12),OTHPR1(6)
     >   ,OTHPR2(6)

      DATA SPRD/.4,.56,.44, .4,.28,.44, .2,.06,.10, 0.,.05,.00, 0.,.05
     >             ,.00, 0.0,0.0,0.02/
      DATA IMAX/0/              !.. Initialize IMAX Reset in FLXCAL

      !.. Transfer neutral densities to the density array
      XN(1)=OXN
      XN(2)=O2N
      XN(3)=N2N
      N2APRD=0.0
      DO K=1,3
      DO IK=1,6
        PEPION(K,IK)=1.0E-15
        PEXCIT(K,IK)=1.0E-15
      ENDDO
      ENDDO

      !.. Cannot calculate PE if no densities
      IF(OXN.LT.1.0E5.OR.N2N.LT.1.0E5) RETURN
      IF(SZADEG.GT.105) RETURN

      !********************************************************************
      !.. Go and get the photoelectron fluxes
       XN2D=0        !.. N(2D) density for calculating N(2D) + e -> 2.5 eV
       XOP2D=0       !.. O+(2D) density for calculating O+(2D) + e -> 3.3 eV
       CALL FLXCAL(IDIM,ALT,SZADEG,
     >   TE,TN,XN,XNE,XN2D,XOP2D,PEFLUX,AFAC,IMAX,DE,EV)
      !***************************************************************

      !........ sample calculation of ion production rates. 
      DO I=1,IMAX
        E=EV(I)
        CALL TXSION(E,SIGIT)                     !.. total ion XS
        CALL SIGEXS(E,TE,XNE,SIGOX,SIGN2,SIGEE)  !.. Total excitation XS
        CALL OXSIGS(E,SIGEX,SIGOX)               !.. OX cross sections

        IF(E.LT.250) N2APRD=N2APRD+0.22*PEFLUX(I)*SIGN2*XN(3)*DE(I) !.. N2(A) prod
        PEXCIT(1,1)=PEXCIT(1,1)+PEFLUX(I)*SIGEX(1)*XN(1)*DE(I)   !.. O(1D) prod
        PEXCIT(1,2)=PEXCIT(1,2)+PEFLUX(I)*SIGEX(2)*XN(1)*DE(I)   !.. O(1S) prod

        !.. Evaluate ionization branching ratios for O+
        CALL OXRAT(E,SPRD(1,1),SPRD(1,2),SPRD(1,3))

        !.. Calculate ion production rates
        DO K=1,3
        DO IK=1,6
          PEPION(K,IK)=PEPION(K,IK)+PEFLUX(I)*SIGIT(K)*XN(K)*SPRD(K,IK)*
     >      DE(I)
        ENDDO
        ENDDO

      EP=E+17
      PEFLX=PEFLUX(I)/12.57
c      WRITE(29,'(3F8.1,1P,22E10.2)') ALT,E,12398/EP,PEFLX,
c     >     PEFLUX(I),(SIGIT(K),K=1,3),T_XS_OX(EP),2.2*T_XS_OX(EP),
c     >     T_XS_N2(EP),PEPION(1,1),PEXCIT(1,1)
      ENDDO

      RETURN
      END
C:::::::::::::::::::::::::: PHOTOELECTRON MODEL  ::::::::::::::::::::::::
C....... This subroutine evaluates the photoelectron flux using the concept
C.......  production frequencies developed by Phil Richards at Utah 
C....... State University March 1984. It supercedes the model described in
C....... JGR, p2155, 1983. Contact EAST::CSPARA::RICHARDS on SPAN network
C------- Some minor updates in April 1992 indicated by C----
C....... I would appreciate any feedback on bugs or clarity and if it 
C....... contributes substantially to a paper, I would appreciate the 
C....... appropriate acknowledgement.
C......       **************** WARNING ****************
C...... This program is constructed to produce reasonable agreement with
C...... the Atmosphere Explorer-E PES fluxes of John Doering (Lee et al.
C...... PSS 1980, page 947). It will NOT give good fluxes if the EUV 
C...... attenuation is greater than about a factor of 7 (AFAC < 0.14).
C...... The model accurately reproduces the measured fluxes very closely
C...... for the case in the test driver at 148 km SZA=53 when AFAC=0.19.
C...... You should compare the output against the Lee et al. 1980 fluxes
C...... periodically as a check. It is doubtful below 140km during the
C...... day and below 200km near sunset. Between 200km & 350km, it should
C...... be good for solar zenith angles < 90 degrees. Above 350 km there
C...... is considerable uncertainty due to neglect of transport but most
C...... models have similar uncertainties at high altitudes due to the 
C...... uncertainty in the conjugate photoelectron flux, and the pitch 
C...... angle distribution.
C
C------ ALT = altitude (km)  { 120 -> 500 }
C------ SZADEG = solar zenith angle  {0 -> 90 degrees ? }
C------ TE, TN = electron, neutral temperatures (K)
C------ XN, XNE = O, O2, N2, and electron densities  (cm-3)
C------ XN2D, XOP2D = N(2D) and O+(2D) densities for electron quenching
C------ (cm-3). You may put these to ZERO if not available.
C------ PEFLUX = photoelectron flux to be returned (eV cm2 sec)-1
C------ AFAC = the solar EUV attenuation warning flag
      SUBROUTINE FLXCAL(IDIM,ALT,SZADEG,
     >  TE,TN,XN,XNE,XN2D,XOP2D,PEFLUX,AFAC,IMAX,DE,EV)
      INTEGER RDIM,IMAX
      REAL EMAX             !.. maximum photoelectron energy.
      PARAMETER (RDIM=84)
      REAL RJOX(RDIM),RJN2(RDIM),XN(3),COLUM(3),PEFLUX(IDIM)
     >  ,DE(RDIM),DELTE(RDIM),EV(RDIM),EN(RDIM),UVFAC,EUV
      COMMON/SOL/UVFAC(59),EUV

      !.. photoelectron production frequencies by 1.0E9. Renormalized below
      !-- O production frequencies
      DATA RJOX/10*19,15,18,14,10,13,9,13,9,7,11,6,26,6,31,6,5,22,4,
     >   4,5,4.04,2.56,1.9,2.28,2.12,0.96,0.24,0.14,0.14,0.1,0.1,0.1
     >   ,0.1,0.1, 10*.05,10*.04,10*.01,10*.02/

      !-- N2 production frequencies
      DATA RJN2/6*40,43,35,35,28,29,21,25,19,19,13,19,16,12,11,7,18,8,
     >  46,27,5,5,5,5,5,5.34,2.92,1.84,2.22,1.62,0.62,0.05,0.05,0.05,
     >  0.05,0.05,0.05,0.05,0.044,10*.02,10*.01,10*.01,10*.01/

      !-- PE energy grid
      DATA EN/0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5,10.5,11.5,12.5,
     >  13.5,14.5,15.5,16.5,17.5,18.5,19.5,20.5,21.5,22.5,23.5,24.5,
     >  25.5,26.5,27.5,28.5,29.5,32.5,37.5,42.5,47.5,52.5,57.5,62.5,
     >  67.5,72.5,77.5,82.5,87.5,92.5,97.5,105,115,125,135,145,155,
     >  165,175,185,195,205,215,225,235,245,255,265,275,285,295,305,
     >  315,325,335,345,355,365,375,385,395,405,415,425,435,445,455,
     >  465,475,485,495/

      !-- PE energy steps
      DATA DELTE/30*1.0,14*5.0,40*10/
	DATA EMAX/286.0/          !..  Maximum PE energy

      SZA = SZADEG/57.29578   !.. convert solar zenith angle to radians

      IF(IMAX.LT.10) THEN
        !.. transfer energy grid to pass back
        DO IE=1,RDIM
          IF(EN(IE).LT.EMAX) IMAX=IE
          DE(IE)=DELTE(IE)
          EV(IE)=EN(IE)
        ENDDO
      ENDIF

      !.. 2.5eV production from electron quenching of N2D
      PN2D=XN2D*XNE*6.0E-10*SQRT(TE/300.0)
      !.. 3.3eV production from electron quenching of O+(2D)
      POP2D=XOP2D*XNE*6.6E-8*SQRT(300./TE)

      CASEL=0.0

      !.. evaluate the neutral column density  &&&&&&&&
      CALL SCOLUM(I,SZA,ALT*1.0E5,TN,XN,COLUM)

      !...... begin flux calculation loop............................
      DO 133 IE=1,IMAX
        I=IMAX+1-IE
        IF(I.LT.1) GO TO 55
        PEFLUX(I)=0.0

        !... evaluate energy of photon responsible for electron at energy EE
        EE=EV(I)
        EP=EE+17
        IF(EE.LT.22) EP=45
        IF(EE.GE.22.AND.EE.LT.28) EP=41
        IF(EE.GE.28.AND.EE.LT.38) EP=49

        !.. evaluate total photoionization cross sections for photon energy EP
        XSOXT=T_XS_OX(EP)         !.. New OX cross section
        XSO2T=2.2*T_XS_OX(EP)     !.. O2 XS is 2.2* O XS
        XSN2T=T_XS_N2(EP)         !.. New N2 cross section

        !... evaluate EUV attenuation factor AFAC
        TAU=COLUM(1)*XSOXT+COLUM(2)*XSO2T+COLUM(3)*XSN2T
        AFAC=EXP(-TAU)

        !..... low energy cascade production from O(1D) and N2* impact
        CASOX=0.0
        IF(EE.LT.10) CASOX=PEFLUX(I+2)*SIGOX*XN(1)
        CASN2=0.0
        IF(EE.LT.6) CASN2=PEFLUX(I+1)*SIGN2*XN(3)

        !..... cascade production from thermal electron degradation
        CASEL=0.0
        IF(I.LT.IMAX) CASEL=PEFLUX(I+1)*SIGEE*XNE

        !... Production from electron quenching of metastables
        EPN2D=0.0
        IF(NINT(EE).EQ.3) EPN2D=PN2D
        EPOP2D=0.0
        IF(NINT(EE).EQ.4) EPOP2D=POP2D

        !.... evaluate cross sections (must be after cascade production)
        CALL SIGEXS(EE,TE,XNE,SIGOX,SIGN2,SIGEE)

        !..... adjust EUV production rate for different period of solar cycle
        CALL FACFLX(EE,UVFAC,FFAC)

        !..... Production of pe's at energy EE, taking into account
        !..... attenuation and EUV variation, and renormalize frequencies

        PRODOX=RJOX(I)*XN(1)*AFAC*FFAC*1.0E-9 
        PRODN2=RJN2(I)*XN(3)*AFAC*FFAC*1.0E-9 

        !..... Sum all the production rates
        PROD=PRODOX+PRODN2+CASEL+CASOX+CASN2+EPN2D+EPOP2D

        !.... total loss through collisions
        RLOSS=SIGOX*XN(1)+SIGN2*XN(3)+SIGEE*XNE

        !....... evaluate photoelectron flux
        PEFLUX(I)=PROD/RLOSS
 133  CONTINUE

 55   RETURN
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE FACFLX(EE,UVFAC,FFAC)
C....... solar UVFAC factors. Correspond to the first 9 wavelengths
C....... TORR et al.[1979] GRL page 771 table 3. UVFAC(9) is for 304A
      REAL UVFAC(59)
      FFAC=(7*UVFAC(9)+UVFAC(8)+0.2*UVFAC(6))/8.2
      IF(EE.GT.30.AND.EE.LE.38) FFAC=(2*UVFAC(7)+.5*UVFAC(5))/2.5
      IF(EE.GT.38.AND.EE.LE.45) FFAC=UVFAC(4)
      IF(EE.GT.45.AND.EE.LE.66) FFAC=UVFAC(3)
      IF(EE.GT.66.AND.EE.LE.108) FFAC=UVFAC(2)
      IF(EE.GT.108) FFAC=UVFAC(1)
      RETURN
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE SIGEXS(E,TE,XNE,SIGOX,SIGN2,SIGEE)
C..... Program for evaluating the total inelastic cross sections
C
C........ loss to thermal electrons ....
      ET=8.618E-5*TE
      SIGEE=(3.37E-12/E**0.94/XNE**0.03)*((E-ET)/
     >   (E-(0.53*ET)))**2.36
C
C...... cross section for o(1d)
      SIGO1D=0.0
      IF(E.GT.1.96) SIGO1D=4E-16*(1-1.96/E)**2/E
C...... total excitation cross section for O excluding O(1D)
      IF(E.LT.25) SIGO=(0.4*E-5)*1.4E-17
      IF(E.GE.25) SIGO=7.0E-17
      IF(SIGO.LT.0.0) SIGO=0.0
C
C...... total excitation cross section for N2......
      IF(E.LT.12) SIGN2=(15.5*E-104.8)*1.7E-18
      IF(E.LT.4.0) SIGN2=5.0E-9*(1-1.4/E)**9 * (1.4/E)**16
      IF(E.GT.11.5) SIGN2=1.4E-16
      IF(SIGN2.LT.0.0) SIGN2=0.0
C
C........ total ionization cross sections from Keiffer and Dunn ....
      SIGION=0.0
      AL=ALOG10(E)
      IF(AL.LT.2.7.AND.AL.GE.1.2) SIGION=-3.6E-16*(AL-1.2)*(AL-3)
      IF(AL.GT.2.7) SIGION=1.2E-14*EXP(-AL*1.6)
      IF(E.LT.50) SIGION=1.0E-16*(0.068*E-1.06)
      IF(SIGION.LE.0.0) SIGION=0.0
C
      SIGOX=SIGO1D+SIGO+0.5*SIGION
      SIGN2=SIGN2+SIGION
      RETURN
      END
C::::::::::::::::::::::: TXSION ::::::::::::::::::::::::::::::::::
C..... total ionization cross sections for O, O2, and N2
C..... ionization cross sections keiffer and dunn ........
C..... The N2+ and O2+ cross sections were modified in April 99 to agree
C..... with the Schram et al. cross sections at high energies
      SUBROUTINE TXSION(E,SIGIT)
      DIMENSION SIGIT(3)

      !... SIGTMP is used for N2+ and O2+ at the high energies
      SIGTMP=1.0E-13*EXP(-2.303*ALOG10(E))

      !... N2+ cross section
      SIGIT(3)=0.0
      IF(E.GT.15.0) SIGIT(3)=1.42E-14*(1-9.0/E)**7.1*E**(-0.7) 
      IF(SIGTMP.LT.SIGIT(3)) SIGIT(3)=SIGTMP
      !... This correction to convert units to cm**2. Keiffer and Dunn page 10
      SIGIT(3)=0.87972*SIGIT(3)

      !... O2+ cross section
      SIGIT(2)=0.0
      IF(E.GT.12.0) SIGIT(2)=1.08E-14*(1-7.0/E)**8.6*E**(-0.65)
      IF(SIGTMP.LT.SIGIT(2)) SIGIT(2)=SIGTMP
      !... This correction to convert units to cm**2. Keiffer and Dunn page 10
      SIGIT(2)=0.87972*SIGIT(2)

      !... O+ cross section from Brook et al. J. Phys. B. Vol 11 p 3115, 1978
      SIGIT(1)=0.0
      IF(E.GT.12.0) SIGIT(1)=7.33E-15*(1-2.0/E)**34.3*E**(-0.7)
      RETURN
      END
C:::::::::::::::::::::::::::::::::::: OXRAT ::::::::::::::::::::::::::::::::
      SUBROUTINE OXRAT(E,R4S,R2D,R2P)
C....... This subroutine returns the electron impact branching ratios
C....... for atomic oxygen from Burnett and Rountree Phys. Rev. A. 20
C....... 1979 page 1468
      R4S=1.0
      R2D=0.0
      R2P=0.0
      EV=E
      IF(E.GT.100.0) EV=100.0
      IF(EV.GT.17) R4S=-1.6E-3*EV+0.56
      IF(EV.GT.17) R2D=1.067E-3*EV+0.2933
      R2P=1-R4S-R2D
         IF(EV.LT.22) THEN
         R2P=0.0
         RTOT=R4S+R2D
         R4S=R4S/RTOT
         R2D=R2D/RTOT
         ENDIF
      RETURN
      END
C::::::::::::::::::::: T_XS_N2 :::::::::::::::::::::::::::
C.... This function calculates the N2 total photoionization
C.... cross section. P. Richards 2003-10-04
      REAL FUNCTION T_XS_N2(EP)
      IMPLICIT NONE
      REAL EP   !... photon energy
      REAL ESAVE
      DATA ESAVE/0.0/

      !.. Wavelength < 20 A, Auger ionization
      IF(EP.GE.600.0) THEN              
        T_XS_N2=0.5E-18
      !.. Wavelength < 31 A, Auger ionization
      ELSEIF(EP.GE.400.0) THEN              
        T_XS_N2=1.0E-18
      !.. Wavelength 31.62 to 23.70 A
      ELSEIF(EP.GE.392.0) THEN
        T_XS_N2=EXP(7.9864*ALOG(EP)-91.6604)
      !.. Wavelength 225 to 125 A
      ELSEIF(EP.GE.55.09) THEN
        T_XS_N2=EXP(-2.3711*ALOG(EP)-29.8142) 
      !.. Wavelength > 225 A
      ELSE
        T_XS_N2=EXP(-1.1077*ALOG(EP)-34.8787)  
      ENDIF

      !..IF(NINT(10*EP).NE.NINT(10*ESAVE)) WRITE(6,'(2F8.1,1P,2E10.2)') 
      !..> 12394.224/EP,EP, T_XS_N2/(3.39E-17*EXP(-0.0263*EP)), T_XS_N2
       ESAVE=EP

      !.. old parameterization
      !..T_XS_N2=3.39E-17*EXP(-0.0263*EP)

      RETURN
      END
C::::::::::::::::::::: T_XS_OX :::::::::::::::::::::::::::
C.... This function calculates the OX total photoionization
C.... cross section. P. Richards 2003-10-04
C.... Samson and Pareek Phys. Rev. A, 31, 1470, 1985

      REAL FUNCTION T_XS_OX(EP)
      IMPLICIT NONE
      REAL EP   !... photon energy
      REAL ESAVE
      DATA ESAVE/0.0/

      !.. NEW parameterization
      IF(EP.GE.500.0) THEN                 
        !.. Wavelength shorter than 25 A, Auger ionization
        T_XS_OX=0.5E-18
      ELSEIF(EP.GE.165.26) THEN                 
        !.. Wavelength shorter than 75 A
        T_XS_OX=EXP(-2.5209*ALOG(EP)-28.8855)
      ELSEIF(EP.GE.55.09) THEN              
        !.. Wavelength between 78 and 256.26 A
        T_XS_OX=EXP(-1.7871*ALOG(EP)-32.6335)
      ELSE
        !.. Wavelength longer than 256.26 A
        T_XS_OX=EXP(-1.3077*ALOG(EP)-34.5556)   
      ENDIF

      !..IF(NINT(10*EP).NE.NINT(10*ESAVE)) WRITE(6,'(2F8.1,1P,2E10.2)') 
      !..> 12394.224/EP,EP, T_XS_OX/(27.2E-18*EXP(-3.09E-2*EP)), T_XS_OX
       ESAVE=EP

      !.. old parameterization
      !.. T_XS_OX=27.2E-18*EXP(-3.09E-2*EP)

      RETURN
      END
C:::::::::::::::::::::: OXSIGS :::::::::::::::::::::::::::::::::::::
      SUBROUTINE OXSIGS(E,SIGEX,SIGEXT)
C....... Inelastic cross sections for electron impact on atomic oxygen
C....... E=electron energy, SIGEX(22)=array of partial cross sections,
C....... SIGEXT=total excitation cross section, and S
      DIMENSION SIGEX(22),SO1D(7)
      DO 9 I=1,22
 9    SIGEX(I)=0.0
      !..- CROSS SECTION FOR O(1D) - New Doering cross section from JGR
      !..- p19531, 1992. Increases production by a factor of 1.13
      DATA SO1D/0.0,0.0,15.0,30.0,44.0,54.0,38.0/
C..      IF(E.GT.6.5) SIGEX(1)=3.77E-15*(1-2.0/E)**4.25/E**1.7
C..      IF(E.LE.7.3) SIGEX(1)=SO1D(NINT(E))*1.0E-18
C
C..... Old cross section of Henry
      IF(E.GT.1.96) SIGEX(1)=4E-16*(1-1.96/E)**2/E
C........ O(1S) cross section: may be double Shyn et al. JGR 1986, 13751
      IF(E.GT.4.17) SIGEX(2)=6.54E-17*(1-SQRT(4.17/E))/E
C....... 1304, 1027 A, Zipf and Erdman JGR 1985, 11088 include cascade.
C....... Direct excitation is half for  1304 (Vaughan and Doering,
C........ JGR 1986, 13755 and 1987 in press)
      IF(E.GE.10) SIGEX(3)=67.6E-17*(E-10)/E**2
C....... 989 cross section from Doering 1987 (1/2 of Zipf)
      IF(E.GE.14) SIGEX(4)=7.0E-17*(1-14/E)/SQRT(E)
      SIGEX(5)=0.38*SIGEX(4)
C....... O(5S) 1356 A Stone And Zipf Corrected By Zipf And Erdman 1985
      !..- reparameterized 1 May 92 using FITXS.FOR (PGR)
      IF(E.GT.10.0) SIGEX(6)=4.867E-12*(1.0-9.0/E)**2.67/ E**4.0
      SIGEXT=SIGEX(1)+(SIGEX(2)+SIGEX(3)+SIGEX(4)+SIGEX(5)+SIGEX(6))
      RETURN
      END
C
C
C.................... RSPRIM.FOR ..................................
C.... This routine evaluates the ionization rates for photon impact
C.... It is based on a FLIP model routine that was modified in August 
C.... 2009 for the chemical equilibrium model by P. richards. 
      SUBROUTINE PRIMPR(IJ,Z,ZOX,ZN2,ZO2,HE,SZA,TN,F107,F107A,N4S)
      IMPLICIT REAL(A-H,O-Z)
      INTEGER IVERT
      REAL Z,ZOX,ZN2,ZO2,HE,SZA,TN,CHI,ZZ,TNJ,TAU,FLUX,HEPLS,FBSBN
     >  ,DISN,TAUGAM,FLUXG,ALTG,XNSIGF,DSPECT,GL,N4S
      REAL COLUM(3),OTHPR1,OTHPR2,OTHPR3(6)
      REAL COLUMN(3),XN(3),PROB(3,6,37),XSNPLS(37),FNITE(37),CLNITE(3)

      !-- common to hold the EUV and photoelectron production rates 
      COMMON/EUVPRD/EUVION(3,12),PEXCIT(3,12),PEPION(3,12),OTHPR1(6)
     >   ,OTHPR2(6)
      COMMON/SIGS/ZFLUX(37),SIGABS(3,37),ZLAM(37),SIGION(3,37),
     > TPOT(3,10),NNI(3),LAMAX
      COMMON/SOL/UVFAC(59),EUV

      DATA LMAX/0/, F107SV/0.0/, IPROBS/0/
      !.. Fluxes for nighttime ion production in the 37 wavelength bins of
      !.. Torr et al GRL 1979. The fluxes are set to reproduce the production
      !.. rates in Strobel et al. PSS, p1027, 1980. Note that most bins are 
      !.. set to zero and that the Strobel production rates are scaled by 
      !.. FNFAC to stabilize the O+ solution below 200 km. Note also that
      !.. the wavelengths in FNITE go from largest (#3=HI) to smallest.
      DATA FNITE/9E5,0.0,9E5,2*0.0,9E6,13*0.0,3E5,8*0.0,3E5,8*0.0/
      DATA FNFAC/1.0/

      !.. UVFAC(58) is left over from FLIP routines for compatibility
      UVFAC(58)=-1.0 
      IF(ABS((F107-F107SV)/F107).GT.0.005) THEN
        !.. update UV flux factors
        CALL FACEUV(UVFAC,F107,F107A)
        CALL FACSR(UVFAC,F107,F107A)
        !.. call params to get solar flux data and cross sections
        CALL PARAMS(0,LMAX)
        F107SV=F107

        !..  find probability for formation of each state  ........
        IF(IPROBS.EQ.0) CALL PROBS(0,PROB,ZLAM,LMAX,NNI)
        IPROBS=1

      ENDIF

      !... initialization of production rates. 1.0E-15 stabilizes 
      !... e density evaluation at low altitudes in CMINOR
      DO 10 IS=1,3
      DO 10 IK=1,12
         EUVION(IS,IK)=1.0E-15
 10   CONTINUE

      DISN=0.0
      DO 687 I=1,6
      OTHPR2(I)=1.0E-15
 687  OTHPR1(I)=1.0E-15
C
C........ Nighttime He+ production is calculated and stored. Attenuated to
C........ avoid excess production at low altitudes
      OTHPR1(2)= 8E-11* EXP(-1.0E-11*ZN2) *HE
      DO 786 I=1,3
 786  COLUM(I)=1.0E+25
      TNJ=TN
      XN(1)=ZOX
      XN(2)=ZO2
      XN(3)=ZN2
      ZZ=Z*1.0E+5
      CHI=SZA
C
C*****  obtain reaction rates from subr rats to get their densities

C....... determine if sun is below the horizon ...
C---- Must now do calculation for night production - Feb 93
      ALTG=(6371.0+Z)*SIN(3.1416-CHI)-6371.0
C....      IF(CHI.GT.1.57.AND.ALTG.LT.85.) RETURN
      IF(Z.GT.1500) RETURN
C
C...... get column densities for scattered light at night  &&&&&&&&
      CALL SCOLUM(IJ,0.0E0,ZZ,TNJ,XN,CLNITE)
C
C...... evaluate the neutral column density  &&&&&&&&
      CALL SCOLUM(IJ,CHI,ZZ,TNJ,XN,COLUMN)
C........ Store the column densities for the 2-Stream program
      COLUM(1)=COLUMN(1)
      COLUM(2)=COLUMN(2)
      COLUM(3)=COLUMN(3)
C
C........ O2 dissociation by Schumann-Runge UV.
C........ OTHPR1(3)= dissociation rate. OTHPR1(5)= Energy
      CALL SCHUMN(IJ,Z,ZO2,COLUMN,OTHPR1(3),OTHPR1(5))
C
C---- Calculate hv + NO ion. freq. from Lyman-a (Brasseur & Solomon)
C---- OTHPR2(2) is photodissociation of NO in the SR bands. 
C---- A small night production from scattered light is included. FREQLY
C---- varies with solar activity using Richards et al. 1994 page 8981
C---- LY_a=2.5E11 (Lean), sigi(NO)=2.0E-18 (Brasseur & Solomon page 329)
      DATA O2LYXS,O2SRXS,FREQSR /1.0E-20,1.0E-21,5.0E-6/
       FREQLY=5.0E-7*(1+4.0E-3*(0.5*(F107+F107A)-80.0))
       OTHPR2(1)=FREQLY*(EXP(-O2LYXS*COLUMN(2))
     >    +0.001*EXP(-O2LYXS*CLNITE(2)))
       OTHPR2(2)=FREQSR*(EXP(-O2SRXS*COLUMN(2))
     >    +0.001*EXP(-O2SRXS*CLNITE(2)))
C
      !..  wavelength loop begins here  ----------
      !..  TAU, TAUN = optical depth for day, night 
      HEPLS=0.0
      DO 6 L=1,LMAX
        TAU=0.
        TAUN=0.0
        DO I=1,3
          TAUN=TAUN+SIGABS(I,L)*CLNITE(I)
          TAU=TAU+SIGABS(I,L)*COLUMN(I)
        ENDDO

        !.. evaluate nighttime flux and daytime flux
        FLUXN=FNFAC*(F107/75.0)*FNITE(L)*EXP(-TAUN)
        FLUX=ZFLUX(L)*EXP(-TAU) + FLUXN
        !..WRITE(9,'(I6,1P,22E10.2)') L,COLUMN(1),COLUMN(3),TAU,EXP(-TAU),
        !..>    FLUX, ZFLUX(L),FLUXN

        !.. he+ production. He+ X-S  = 0.25 N2  X-S. HEPRDN = nite He+
        IF(ZLAM(L).LT.500.) HEPLS=HEPLS+HE*0.25*SIGION(3,L)*FLUX

        !-- hv + N -> N+ + e. ion. freq. Richards et al. JGR 1994 page 8989
        DATA XSNPLS/6*0.0,.211,10.294,11.171,10.961,11.244,11.323,12.098
     >  ,13.265,12.423,11.951,11.212,11.798,11.758,11.778,11.772,11.503
     >  ,11.016,10.578,9.556,8.15,8.302,7.298,6.413,6.399,5.192,5.725
     >  ,4.787,3.778,2.3,.878,.286/

        OTHPR2(3)=OTHPR2(3)+XSNPLS(L)*1.0E-18*FLUX*N4S

        IF(ZLAM(L).GE.600.0) THEN
          !...... calculation of total euv absorption-ionization.....
          FBSBN=FLUX*(SIGABS(3,L)-SIGION(3,L))*XN(3)
          !.. Save energy absorbed in the photodissociative process
          OTHPR1(4)=OTHPR1(4)+1.24E+4*FBSBN/ZLAM(L)
          !.. production on atomic nitrogen by dissociation
          DISN=DISN+FBSBN
          !..      IF(J.EQ.1) WRITE(6,95) L,ZLAM(L),TAU,FLUX,FBSBN,DISN,HEPLS
          !95   FORMAT(I4,F9.1,1P,22E9.1)
          !.. take into account the large n2 absorption of lyman gamma(972.54)
          IF(NINT(ZLAM(L)).EQ.975) THEN
             TAUGAM=370E-18*COLUMN(3)
             IF(TAUGAM.GT.70.0)TAUGAM=70.0
             FLUXG=UVFAC(34) *0.82E+9 *EXP(-TAUGAM)
             DISN=DISN+FLUXG*370E-18*XN(3)
           ENDIF
         ENDIF

        !***** species loop begins here *****
        DO 304 I=1,3
          XNSIGF=XN(I)*SIGION(I,L)*FLUX
          K1=NNI(I)
 
          !.. dspect=# ions formed by w-l l by ionization of k state of species i
          DO 302 K=1,K1
            DSPECT=XNSIGF*PROB(I,K,L)
            !.. store ion production rates .....
            EUVION(I,K)=EUVION(I,K)+DSPECT

            !.. calculation of ion heating rate......
            EUVION(1,10)=EUVION(1,10)+DSPECT*TPOT(I,K)

 302      CONTINUE
 304    CONTINUE
 6    CONTINUE
C
      !..---   wavelength loop ends here   -----------
C
C.........Store UV disoc of N2 2 atoms produced for every dissociation
      OTHPR1(1)=2.0*DISN
C........ Transfer He+ production to storage
      OTHPR1(2)=OTHPR1(2)+HEPLS
C
 777  RETURN
      END
C:::::::::::::::::::::::::::: SCOLUM ::::::::::::::::::::::::::::::::::
C.... this routine evaluates the neutral column density for O, O2, and N2
C.... see Smith & Smith JGR 1972 p 3592
C.... chi=solar zenith angle, RE & GE radius and grav constant for earth
C.... Modified by P. Richards January 2010 to eliminate need for calling
C.... the MSIS model at grazing incidence
      SUBROUTINE SCOLUM(J,CHI,Z,TN,XN,COLUMN)
      IMPLICIT NONE
      INTEGER I,J
      REAL ZG,CHI,Z,TNJ,ALTG,GE,GR,RE,RP
      REAL SH,XP,Y,ERFY2,CHAPFN,RG,HG,XG,EM,F,G,A,B,C,D,GL
      REAL TN,XI,TINF,GTN
      REAL XN(3),COLUMN(3),SN(3),M(3),DG(9),T(2),GN(3)
      DATA A,B,C,D,F,G/1.0606963,0.55643831,1.0619896,1.7245609
     >  ,0.56498823,0.06651874/
      DATA SN/0.0,0.0,0.0/
      DATA    EM   ,   M(1) , M(2) , M(3) ,  RE   , GE
     >    / 1.662E-24 ,   16. ,  32. ,  28. ,6.357E8, 980/
      DATA T,ALTG,ERFY2/0.0,0.0,0.0D0,0.0D0/
      DATA DG/9*0.0/

      DO I=1,3
        SN(I)=0.0
        COLUMN(I)=1.E+25
      ENDDO

      TNJ=TN     !.. Avoids changing Tn at grazing incidence

      IF(CHI.LT.1.5708) GO  TO 2938      !.. is sza>90.0 degrees

      !..Grazing incidence parameters 
      ALTG=(6371.0E5+Z)*SIN(3.1416-CHI)-6371.0E5
      IF(ALTG.GE.85*1.0E5) THEN
        ZG=ALTG*1.E-5

        !.. Bates-Walker temperature
        XI=(ZG-120.0)*(6357.0+120.0)/(6357.0+ZG)
        TINF=MAX(TN,500.0)   !.. Crude TINF
        GTN=MAX(TINF-(TINF-300.0)*EXP(-0.025*XI),180.0)

        !.. Neutral densities are extrapolated from altitude to grazing
        !.. altitude. Weighted average Tn and GTn is used 
        GR=GE*(RE/(RE+Z))**2   !.. gravity
        DO I=1,3
          GN(I)=XN(I)*EXP((Z-ALTG)/
     >      ((1.38E-16*(TN+GTN*2)/3)/(EM*M(I)*GR)))
        ENDDO
        !..   WRITE(88,'(6F8.2,1P,22E10.2)') Z/1.0E5,ZG,CHI*180/3.1416,TN,GTN
        !.. >      ,TNJ,((XN(I),GN(I),SN(I)),I=1,3)
        !.. Make sure that grazing incidence density is not lower than MSIS
        !.. This is for using non MSIS densities like CTIPe
        TNJ=GTN
        DO I=1,3
          SN(I)=GN(I)
          IF(SN(I).LT.XN(I)) SN(I)=XN(I)
        ENDDO
      ELSE
        RETURN
      ENDIF
      !.. sn(1)=o , sn(2)=o2 , sn(3)=n2 , tnj=tn,  gr=gravity, rp=distance
      !.. to pt p, sh=scale height, rg=distance to pt g, hg=scale height at g

 2938 CONTINUE
      GR=GE*(RE/(RE+Z))**2
      RP=RE+Z
      !.. Calculate column densities for each species
      DO 10 I=1,3
        SH=(1.38E-16*TNJ)/(EM*M(I)*GR)
        XP=RP/SH
        Y=SQRT(0.5*XP)*ABS(COS(CHI))
        IF(Y.GT.100.0) WRITE(6,100) I,Z/1.0E5,CHI*57.3,TNJ,EM,M(I),GR,RP
 100    FORMAT('WARNING, Y IN COLUMN(I) > 100',I4,1P,9E10.2)
        IF(Y.GT.8) ERFY2=F/(G+Y)
        IF(Y.LT.8) ERFY2=(A+B*Y)/(C+D*Y+Y*Y)

 4      IF(CHI.GT.1.5708)GO  TO 2
        CHAPFN=SQRT(0.5*3.1416*XP)*ERFY2
        COLUMN(I)=XN(I)*SH*CHAPFN
        GO TO 10

 2      RG=RP*SIN(3.1416-CHI)
        HG=1.38E-16*TNJ/
     >    (EM*M(I)*980.*(6371.E5/(6371.E5+ALTG))**2)
        XG=RG/HG
        COLUMN(I)=SQRT(0.5*3.1416*XG)*HG*(2.0*SN(I)-XN(I)*ERFY2)
 10   CONTINUE
      RETURN
      END
C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE PARAMS(ISW,LMAX)
C........ this program determines the cross sections, solar fluxes, and
C........ given in m. torr et al g.r.l 1979 p771, table 2 and 3. but
C........ the longer wavelengths come first
      COMMON/SIGS/ZFLUX(37),SIGABS(3,37),ZLAM(37),SIGION(3,37),
     > TPOT(3,10),NNI(3),LAMAX
      COMMON/SOL/UVFAC(59),EUV
      DIMENSION  X1(111),X2(111),X3(18),ZLX(37),ZFX(37)
C
C....... ionization potentials for o,o2 and n2 see kirby et al note the
C....... o2 2(pi)u and 2(sigma-)u , and n2 f2(sigma)u pots are guesses
C....... the sixth n2 potential is for dissociation
      DATA X3/13.6,16.9,18.6,28.5,40.,0.0,12.1,16.5,18.2,20.,
     > 25.,0.,15.6,16.7,18.8,25.,29.,37./
C........ wavelength data. average is taken for bands
      DATA ZLX/1025.,1031.91,1025.72,975.,977.02,925.,875.,825.,775.,
     > 789.36,770.41,765.15,725.,703.36,675.,625.,629.73,609.76,575.,
     > 584.33,554.31,525.,475.,465.22,425.,375.,368.07,325.,303.78,
     > 303.31,275.,284.15,256.3,225.,175.,125.,75./
C........ fluxes from table 3. these are for 74113. just replace this data
C........ for other years in the table. note!!!! flux doubled for lambda<250
C........ shortest wavelenghts have been tripled
      DATA ZFX/2.4665,2.1,3.5,1.4746,4.4,3.,3.537,1.625,.758,.702,
     > .26,.17,.141,.36,.23,.342,1.59,.53,.357,1.27,.72,.452,.285,
     > .29,.383,.314,.65,.965,6.9,.8,1.679,.21,.46,3.1,4.8,.45,1.2/
C........ absorption cross sections -- o first ,o2, then n2
      DATA X1/5*0.0,1.315,4.554,3.498,5.091,3.749,3.89,4,10.736,11.46
     > ,17.245,13.365,13.4,13.4,13.024,13.09,12.59,12.059,12.127,11.93
     > ,11.496,9.687,9.84,8.693,7.7,7.68,6.461,7.08,6.05,5.202,3.732
     > ,1.839,.73,  1.346,1.0,1.63,21.108,18.73,12.817,8.562,16.631
     > ,22.145,26.668,18.91,20.8,28.535,27.44,21.919,26.017,32.06
     > ,28.07,26.61,22.79,26.04,24.606,23.101,21.91,20.31,18.118
     > ,18.32,17.438,16.81,16.8,14.387,15.79,13.37,10.9,7.509,3.806
     > ,1.316,  3*0.0,50.988,2.24,9.68,20.249,16.992,33.578,16.487
     > ,14.18,120.49,24.662,26.54,31.755,23.339,23.37,22.79,22.787
     > ,22.4,24.13,24.501,23.471,23.16,21.675,16.395,16.91,13.857
     > ,11.7,11.67,10.493,10.9,10.21,8.392,4.958,2.261,0.72/
C....... ionization cross sections 
      DATA X2/5*0.0,1.315,4.554,3.498,5.091,3.749,3.89,4,10.736,11.46
     > ,17.245,13.365,13.4,13.4,13.024,13.09,12.59,12.059,12.127,11.93
     > ,11.496,9.687,9.84,8.693,7.7,7.68,6.461,7.08,6.05,5.202,3.732
     > ,1.839,.73,  .259,0.0,1.05,13.94,15.54,9.374,5.494,6.413,10.597
     > ,10.191,8.47,11.72,23.805,23.75,21.306,24.937,31.1,26.39
     > ,26.61,22.79,26.04,24.606,23.101,21.91,20.31,18.118
     > ,18.32,17.438,16.81,16.8,14.387,15.79,13.37,10.9,7.509,3.806
     > ,1.316,  8*0.0,14.274,8.86,8.5,65.8,15.06,25.48,29.235
     > ,23.339,23.37,22.79,22.787
     > ,22.4,24.13,24.501,23.471,23.16,21.675,16.395,16.91,13.857
     > ,11.7,11.67,10.493,10.9,10.21,8.392,4.958,2.261,0.72/
C
      NNI(1)=5
      NNI(2)=5
      NNI(3)=6
      LMAX=37
      IF(ISW.NE.0) WRITE(17,95)
 95   FORMAT(/5X,'EUV fluxes, Photoabsorption, and Photoionization ',
     >  'Cross sections',
     > /4X,'I',5X,'lam',5X,'flux',4X,'sigaOX',3X,'sigaO2'
     > ,3X,'sigaN2',3X,'sigiOX',3X,'sigiO2',3X,'sigiN2',3X,'UVfac')
C
      DO 20 L=1,LMAX
      ZLAM(L)=ZLX(L)
      FFAC=UVFAC(LMAX+1-L)
      IF(ZFX(L).LT.100) ZFLUX(L)=ZFX(L)*1.0E+9*FFAC
      !..- setting up ionization potentials
      IF(L.LE.6)THEN
         TPOT(1,L)=X3(L)
         TPOT(2,L)=X3(6+L)
         TPOT(3,L)=X3(12+L)
      ENDIF
      !..- setting up cross sections
      DO 10 IS=1,3
      IN=LMAX*(IS-1)+L
      SIGABS(IS,L)=X1(IN)*1.0E-18
      SIGION(IS,L)=X2(IN)*1.0E-18
      IF(SIGABS(IS,L).LT.SIGION(IS,L)) SIGABS(IS,L)=SIGION(IS,L)
 10   CONTINUE
C
      IF(ISW.EQ.0) GO TO 20
      WRITE(17,90) L,ZLAM(L),ZFLUX(L),(SIGABS(I,L),I=1,3)
     > ,(SIGION(I,L),I=1,3),FFAC
 20   CONTINUE
C
      IF(ISW.EQ.0) RETURN
      WRITE(17,94)
 94   FORMAT(/5X,' Ionization potentials for O, O2, N2'
     > ,/2X,'4S   2D   2P   4P   2P*  -   X2   a+A  b4   B2   dis  -'
     > ,'  X2   A2   B2   C2   F2   2s')
 60   WRITE(17,91) ((TPOT(I,J),J=1,6),I=1,3)
C
      RETURN
 90   FORMAT(1X,I4,F9.2,1P,22E9.2)
 91   FORMAT(22F5.1)
      END
C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE PROBS(ISW,PROB,ZLAM,LMAX,NNI)
C.... program for finding branching ratios (probabilities for various ion
C.... and molecular states) of o,o2,n2
C.... ---refs--- m. torr et al grl 1979 page 771, kirby et al atomic data
C.... and nuclear tables 1979 23,page 63
      DIMENSION YO(37,5),PROB(3,6,37),ZLAM(37),NNI(3)
C...... coefficients of o ionization cross sections from torr et al
C..... table 2
      DATA YO/.19,.486,.952,1.311,1.539,1.77,1.628,1.92,1.925,2.259
     > ,2.559,2.523,3.073,3.34,3.394,3.421,3.65,3.92,3.62,3.61,3.88,4.25
     > ,5.128,4.89,6.739,4.0,3.89,3.749,5.091,3.498,4.554,1.315,5*0.0
     > ,.206,.529,1.171,1.762,2.138,2.62,2.325,2.842,2.849,3.446,3.936
     > ,3.883,4.896,5.37,5.459,5.427,5.67,6.02,5.91,6.17,6.29,6.159
     > ,11.453,6.57,3.997,12*0.0, .134,.345,.768,1.144,1.363,1.63
     > ,1.488,1.92,1.925,2.173,2.558,2.422,2.986,3.22,3.274,3.211,3.27
     > ,3.15,3.494,3.62,3.23,2.956,0.664,14*0.0,  .062,.163,.348,.508
     > ,.598,.71,.637,.691,.693,.815,.787,.859,.541,24*0.0, .049,.13
     > ,.278,.366,.412,.35,.383,.307,.308,28*0.0/
C
C....... production of o states from torr et al table 2 (yo array)
C....... need to reverse order of yo to correspond with lambda
      DO 10 L=1,LMAX
      LL=LMAX+1-L
      SUM=YO(LL,1)+YO(LL,2)+YO(LL,3)+YO(LL,4)+YO(LL,5)
      DO 20 I=1,5
      PROB(1,I,L)=0.0
 20   IF(SUM.NE.0.0) PROB(1,I,L)=YO(LL,I)/SUM
 10    CONTINUE
C
C....... call separate subroutines for o2 and n2 probabilities
      DO 30 L=1,LMAX
      CALL PROBO2(1,L,ZLAM(L),PROB,NNI(2))
      CALL PROBN2(1,L,ZLAM(L),PROB,NNI(3))
 30   CONTINUE
C
      IF(ISW.EQ.0) RETURN
      WRITE(17,95)
 95   FORMAT(/5X,' Photoionization branching ratios for O, O2, N2'
     > ,/3X,'Lam    4S   2D   2P   4P   2P*   -   X2   a+A  b4   B2 '
     > ,'  dis   -  X2   A2   B2   C2   F2   2s')
      DO 50 L=1,LMAX
 50   WRITE(17,90) ZLAM(L),((PROB(IS,J,L),J=1,6),IS=1,3)
 90   FORMAT(F8.2,22F5.2)
       RETURN
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
         SUBROUTINE PROBN2(ISW,L,ZLAM,PROB,JPTS)
C...... the n2 probabilities are taken from kirby et al tables b and c
C...... the yield of n+ is determined first then the remaining portion
C...... of the cross section is distributed amongst the n2+ ion states
C...... (x,a,b). the dissociation yield is divided between the 3 higher
C...... energy states according to wight et al. j.phys. b, 1976
C...... the 2 other states of kirby et al are not included
C
      DIMENSION A(6),B(6),X(14),Y(14,6),PROB(3,6,37)
      DATA IPTS/14/
      DATA X/50.,210.,240.,280.,300.,332.,428.,500.,600.,660.,660.01,
     > 720.,747.,796./
      DATA Y/5*.32,.3,.46,.404,.308,.308,.308,.42,1.,1.,5*.55,
     > .52,.46,.506,2*.589,.692,.58,2*.0,5*.13,.12,.08,
     > .09,.103,.103,4*0.0,3*0.0,.05,.1,.15,.83,1.,6*.0,3*.0,
     > .3,.4,.79,.17,7*.0,3*1.,.65,.5,.06,8*.0/
C
C...... if zlam is too big set equal to x(max)
      YLAM=ZLAM
      !.. Prevent divide by zero
      IF(ZLAM.GT.X(14)) YLAM=X(14)-1
      IF(ZLAM.LT.X(1)) YLAM=X(1)+1

       YIELD=0.0
C...... determine yield of n+, and store in prob array
       CALL YLDISS(1,YLAM,YIELD)
C
       DO 10 I=1,IPTS
C kjh 6/22/92   NOTE:  I realize the following statement is strange
C   looking, but its purpose is to prevent the CRAY compiler from
C   vectorizing this loop.  (Which it does incorrectly).
      if(i.eq.25)write(6,*)' '
      IF(YLAM.GT.X(I).AND.YLAM.LE.X(I+1))  GO TO 20
 10   CONTINUE
 20   SUM=0.0
C...... fit straight line between points
      DO 30 J=1,JPTS
      A(J)=(Y(I+1,J)-Y(I,J))/(X(I+1)-X(I))
      B(J)=Y(I,J)-A(J)*X(I)
 30   CONTINUE
C...... determine probabilities of n2+ states
      DO 40 J=1,JPTS
      IF(J.LE.3) PROB(3,J,L)=(A(J)*YLAM+B(J))*(1-YIELD)
      IF(J.GT.3) PROB(3,J,L)=(A(J)*YLAM+B(J))*YIELD
      SUM=SUM+PROB(3,J,L)
 40   CONTINUE
C
      IF(SUM.EQ.0.0) RETURN
C....... normalise probabilities
      DO 50 J=1,JPTS
 50   PROB(3,J,L)=PROB(3,J,L)/SUM
      RETURN
      END
C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
         SUBROUTINE YLDISS(ISW,ZLAM,YIELD)
C..... determination of dissociative yield of n+, refer to kirby et al
C..... page 66 and table b
      DIMENSION X(9),Y(9)
      DATA IPTS/9/
      DATA X/50.,210.,240.,302.,387.,477.,496.,509.,2000./
      DATA Y/.36,.36,.346,.202,.033,.041,.024,0.0,0.0/
C
C
       DO 10 I=1,IPTS
C kjh 6/22/92   NOTE:  I realize the following statement is strange
C   looking, but its purpose is to prevent the CRAY compiler from
C   vectorizing this loop.  (Which it does incorrectly).
      if(i.eq.25)write(6,*)' '
      IF(ZLAM.GE.X(I).AND.ZLAM.LT.X(I+1))  GO TO 20
 10   CONTINUE
 20   IF(ZLAM.GT.387.AND.ZLAM.LT.477) GO TO 40
C....... linear interpolation
      YIELD=(ZLAM-X(I))/(X(I+1)-X(I))*(Y(I+1)-Y(I))+Y(I)
      GO TO 30
C...... parabolic interpolation see formula page 66 kirby et al
 40   YIELD=.0329+8.13E-6*(ZLAM-442)**2
 30   RETURN
      END
C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
         SUBROUTINE PROBO2(ISW,L,ZLAM,PROB,JPTS)
C....... o2 branching ratios are taken from kirby et al table d
C....... columns 4 & 9 are combined. columns 5,6,7&8 are combined
      DIMENSION A(5),B(5),X(20),Y(20,5),PROB(3,6,37)
      DATA IPTS,X/20,304.,323.,454.,461.,504.,537.,556.,573.,584.,598.
     >  ,610.,637.,645.,662.,684.,704.,720.,737.,774.,1026./
      DATA Y/.365,.374,.432,.435,.384,.345,.356,.365,.306,.23,.235,.245,
     > .34,.27,.482,.675,.565,.565,1.,1.,.205,.21,.243,.245,.27,.29,
     > .23,.27,.33,.295,.385,.35,.305,.385,.518,.325,.435,.435,2*.0,
     > .125,.124,.12,.12,.126,.13,.225,.216,.21,.375,.305,.37,.33,.345,
     > 6*.0,.055,.167,.11,.105,.194,.234,.189,.149,.155,.103,.075,.036
     > ,.025,7*0.,.25,.125,.095,.95,.026,15*0./
C
C...... if zlam is too big set equal to x(max)
      YLAM=ZLAM
C...... if zlam is outside range of data values set equal to max or min
      IF(ZLAM.GT.X(20)) YLAM=X(20)
      IF(ZLAM.LE.X(1)) YLAM=X(1)+1.E-3
C
       DO 10 I=1,IPTS
C kjh 6/22/92   NOTE:  I realize the following statement is strange
C   looking, but its purpose is to prevent the CRAY compiler from
C   vectorizing this loop.  (Which it does incorrectly).
      if(i.eq.25)write(6,*)' '
      IF(YLAM.GT.X(I).AND.YLAM.LE.X(I+1))  GO TO 20
 10   CONTINUE
 20   SUM=0.0
C
      DO 30 J=1,JPTS
      A(J)=(Y(I+1,J)-Y(I,J))/(X(I+1)-X(I))
      B(J)=Y(I,J)-A(J)*X(I)
      SUM=SUM+A(J)*YLAM+B(J)
 30   CONTINUE
C
      DO 40 J=1,JPTS
      PROB(2,J,L)=(A(J)*YLAM+B(J))/SUM
 40   CONTINUE
C
      RETURN
      END
C:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE SCHUMN(J,Z,ZO2,COLUMN,SCHUPR,SCHUHT)
C......... production of o(1d) by schumann-runge bands
C......... The fluxes are from Torr et al. GRL 1980 p6063. Scaling is
C......... done using UVFAC which may be set according to F10.7 cm flux
C......... may be done in FACEUV
      IMPLICIT REAL(A-H,O-Z)
      REAL Z,ZO2,SCHUPR,SCHUHT,COLUMN,HSRX,FLD
      COMMON/SOL/UVFAC(59),EUV
      DIMENSION COLUMN(3),SRFLUX(8),SRXS(8),SRLAM(8)
      DATA SRFLUX/2.4,1.4,.63,.44,.33,.17,.12,.053/
      DATA SRXS/.5,1.5,3.4,6,10,13,15,12/
      DATA SRLAM/1725,1675,1625,1575,1525,1475,1425,1375/
C
C........ lmax=# of lambdas in sub. primpr: schuht=heating: schupr=o(1d) prod
      LMAX=37
C
      DO 505 LSR=1,8
C......... photoabsorption cross section
      SRXSCT=1.0E-18*SRXS(LSR)
      HSRX=SRXSCT*COLUMN(2)
      IF(HSRX.GT.70)HSRX=70
C........ attentuated solar flux
      FLD=UVFAC(LMAX+LSR)*1.E+11*SRFLUX(LSR)*EXP(-HSRX)
C............ neutral heating SCHUHT and photodissociation rate SCHUPR
      SCHUHT=SCHUHT+1.24E+4*(FLD*SRXSCT)*ZO2/SRLAM(LSR)
      SCHUPR=SCHUPR+FLD*SRXSCT
      !IF(JTI.EQ.0) WRITE(24,90) LSR,SRXSCT,FLD,SCHUPR,COLUMN(2),FLD,
      !>   UVFAC(LMAX+LSR)
 505  CONTINUE
C
      SCHUPR=ZO2*SCHUPR
 90   FORMAT(2X,I5,1P,9E9.1)
      JTI=1
      RETURN
      END
C:::::::::::::::::::::::::::::::: FACEUV :::::::::::::::::::::::
      SUBROUTINE FACEUV(UVFAC,F107,F107A)
C----- This routine uses the EUV scaling from Richards et al.[1994]
C----- The EUVAC flux model is based on the F74113 solar reference
C----- spectrum and Hinteregger's scaling factors. This subroutine
C----- just provides the scaling factors as a function of the proxy
C----- (F107+F107A)/2
      DIMENSION UVFAC(59),HFG200(37)
      DATA HFG200/2.202,1.855,2.605,3.334,1.333,17.522,4.176,4.0
     >  ,1.4,3.694,1.791,5.385,1.889,1.899,3.427,2.051,1.392,1.619
     >  ,1.439,2.941,1.399,2.416,1.512,1.365,1.570,1.462,2.537,1.393
     >  ,1.572,1.578,1.681,1.598,1.473,1.530,1.622,1.634,1.525/

      !--  Test to see if need to scale - see DATRD2 subroutine      
      IF(NINT(UVFAC(58)).EQ.-1.OR.NINT(UVFAC(58)).EQ.-3) THEN
         !........... EUV scaling
         F107AV=(F107+F107A)*0.5
         DO 50 I=1,37
         A=(HFG200(I)-1)/120.0
         B=1-A*80.0
         UVFAC(I)=A*F107AV+B
         IF(UVFAC(I).LT.0.8) UVFAC(I)=0.8
 50      CONTINUE
      ENDIF
      RETURN
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
      SUBROUTINE FACSR(UVFAC,F107,F107A)
C........ The Schumann-Runge factors are scaled according to F10.7
C........ from Torr et al. GRL 1980 p6063
      DIMENSION UVFAC(59),SRFLUX(8),SRA(8),SRB(8)
      !............. Schumann-Runge scaling
      DATA SRFLUX/2.4,1.4,.63,.44,.33,.17,.12,.053/
      !...... first two SRA and SRB values out of order in Marsha's paper
      DATA SRA/25.5,20.7,13.2,11.6,11.3,7.86,7.68,4.56/
      DATA SRB/222.,129.,53.4,36.0,25.0,11.3,6.35,2.05/
C
C----  Test to see if need to scale - see DATRD2 subroutine      
      !IF(NINT(UVFAC(58)).EQ.-1.OR.NINT(UVFAC(58)).EQ.-3) THEN
C
         DO 505 I=38,50
            LSR=I-37
            UVFAC(I)=1.0
            IF(LSR.LE.8)
     >      UVFAC(I)=(SRA(LSR)*1.0E7*F107+SRB(LSR)*1.0E9)/SRFLUX(LSR)
     >           /1.0E11
 505     CONTINUE
      !ENDIF
      RETURN
      END
C::::::::::::::::::::::::: EPHEM ::::::::::::::::::::::::::::::::::::::
      SUBROUTINE EPHEM(IDAY,ETRAN)
      DIMENSION EPTRAN(26)
      DATA EPTRAN/4338,4374,4398,4404,4392,
     >  4374,4344,4320,4302,4296,4302
     > ,4320,4338,4356,4356,4344,4320
     > ,4290,4260,4236,4218,4224,4248,4284
     > ,4320,4350/
      ANUM=(MOD(IDAY,1000)+15.)/15.
      INUM=ANUM
      FRAC=ANUM-INUM
      ETRAN=(EPTRAN(INUM)*(1.0-FRAC)+EPTRAN(INUM+1)*FRAC)*10.
      RETURN
      END
C::::::::::::::::::::::::::: SOLDEC :::::::::::::::::::::::::
C...... This routine calculates the solar declination (DELTA radians)
C...... and ephemeris transit time (ETRAN in secs). ETRAN is the time
C...... the sun is overhead in Greenwich
C...... REFERENCE - page 484 "Explanatory Supplement to the Astronomical
C...... Almanac" Kenneth Seidelmann, University Science Books, 20 Edgehill 
C...... Road, Mill Valley, CA 94941, 1992
C...... IDAY is yyyyddd (eg 1988015 = feb 15), UT is the universal time
C...... in hours (0-24) 
       SUBROUTINE SOLDEC(IDAY,UT,DELTA,ETRAN)
      !.... Find day of year (0-366), and year (1996), then Julian day
       INTEGER JD,DAYNUM
       REAL T,YEAR,UT,L,G,LAMBDA,EPSIL,E,GHA,DELTA,SD,ETRAN,DTOR
       DOUBLE PRECISION DJD,DUT
       DATA DTOR/57.29578/   ! degrees to radians
      !..... Recover year and date and make sure UT is less than 24
       DAYNUM=MOD(IDAY,1000)
       YEAR=(IDAY-DAYNUM)/1000
       JD=INT(365.25*(YEAR-1900)+DAYNUM)+2415020      ! Julian day
       DJD=JD                                ! extra precision needed         
       DUT=UT
       T=(DJD+DUT/24.0-2451545.0)/36525.0         ! # of centuries
      !..     WRITE(6,*) DAYNUM,YEAR,JD,UT
       L=AMOD(280.460+36000.770*T,360.0)              ! aberration
       G=AMOD(357.528+35999.050*T,360.0)              ! mean anomaly
      !...... LAMBDA= ecliptic longitude. DELTA=obliquity of the ecliptic.
       LAMBDA=AMOD(L+1.915*SIN(G/DTOR)+0.020*SIN(2.0*G/DTOR),360.0)
       EPSIL=23.4393-0.01300*T
      !...... Equation of time. Time difference between noon and overhead sun
       E=-1.915*SIN(G/DTOR)-0.020*SIN(2.0*G/DTOR)
     >   +2.466*SIN(2*LAMBDA/DTOR)-0.053*SIN(4*LAMBDA/DTOR)
       GHA=15*UT-180+E                    ! Greenwich hour angle
       DELTA=ASIN(SIN(EPSIL/DTOR)*SIN(LAMBDA/DTOR))  ! solar declination
       SD=0.267/(1-0.017*COS(G/DTOR))    ! 
       ETRAN=(12-E/15)*3600 ! Ephemeris transit time in secs for FLIP
       RETURN
       END
C::::::::::::::::::::::: GETLTSZA ::::::::::::::::::::::::::::
      SUBROUTINE GETLTSZA(IDAY,SEC,GLATR,GLOND,SAT,SZA,DEC)
      IMPLICIT NONE
      INTEGER IDAY      !.. Day of year in form YYYYDDD
      REAL SEC          !.. UT in seconds
      REAL GLATR,GLOND  !.. Geographic Latitude and Longitude
      REAL SAT          !.. Solar Apparent time
      REAL SZA,SZA_ARG  !.. Solar zenith angle & argument 
      REAL DEC          !.. Solar declination
      REAL HH           !.. Hour angle
      REAL ETRAN        !.. ephemeris transit time

      CALL EPHEM(IDAY,ETRAN)  !.. get ephemeris transit
      !..... Get solar declination and ephemeris transit time

      CALL SOLDEC(IDAY,SEC/3600.0,DEC,ETRAN)

      !...... Evaluate Solar apparent time
      SAT=(SEC-ETRAN+43200.0)/3600+GLOND/15.0
      IF(SAT.LT.0) SAT=SAT+24
      IF(SAT.GT.24) SAT=SAT-24

      !...... Evaluate Solar zenith angle
      HH=(SAT-12.)*15.0*3.141592654/180.       !.. hour angle
      !.. Evaluate argument for ACOS and test because roundoff error 
      !.. may cause invalid ACOS argument      
      SZA_ARG=COS(GLATR)*COS(DEC)*COS(HH)+SIN(GLATR)*SIN(DEC)
      IF(SZA_ARG.GT.1.0) SZA_ARG=1.0
      SZA=ACOS(SZA_ARG)                 !.. solar zenith angle
      RETURN
      END
C::::::::::::::::::::::::::::::::: ACTUAL_DAY:::::::::::::::::::::::::
C...... Since IDAY does not change and UT continually increases, need to
C...... evaluate actual day (ID) and UT (SX) for MSIS, HWM, and IRI.
C...... Modified by P. Richards in November 2008 to allow for long runs
      SUBROUTINE ACTUAL_DAY(IDAY,    !.... FLIP start day YYYYDDD
     >                       SEC,    !.... Current UT in secs (continuous)
     >                        ID,    !.... actual day YYYYDDD (output) 
     >                        SX)    !.... UT (0-24) in secs (output)
      
      IMPLICIT NONE
	INTEGER SDIM                  !.. Dimension for array
	PARAMETER(SDIM=11)
      INTEGER I,IWR                 !.. Loop control, IWR= write control 
      INTEGER IDAY,ID               !.. FLIP start YYYYDDD, ID= current YYYYDDD
      INTEGER YSTART,DSTART         !.. Start year YYYY and start day DDD
      INTEGER NYRS,NDAYS,NSECS(SDIM)  !.. # of years, days, and seconds in these years
      INTEGER IDAYS                 !.. # Number of days in run so far
      REAL SEC,SX                   !.. UT in secs, actual UT in secs (output)
	DATA IWR/0/

      !.. Check the run is not too long
      IF(SEC.GT.SDIM*3.16E+7) THEN
         WRITE(6,55) SDIM
         CALL RUN_ERROR    !.. print ERROR warning in output files
         STOP
      ENDIF
 55   FORMAT(2X,'** ERROR: FLIP cannot do more than',I3,' year run **')

      YSTART=IDAY/1000               !.. Determine the start year YYYY
      DSTART=MOD(IDAY,1000)          !.. Determine the start day DDD

      !.. Determine the number of days and seconds simulated so far 
      !.. in order to determine the current year and the UT in that year
      NDAYS=0
      DO I=1,SDIM
        IF(MOD(YSTART+I-1,4).EQ.0) THEN     !.. leap year
           NDAYS=NDAYS+366
        ELSE
           NDAYS=NDAYS+365                  !.. normal year
        ENDIF

        !.. Time elapsed since the start day in seconds
        NSECS(I)=(NDAYS-DSTART+1)*24*3600

        !.. Jump out of loop when the time exceeds the current FLIP run time
        IF(NSECS(I).GT.INT(SEC)) THEN
           NYRS=I-1
           GOTO 10
        ENDIF
      ENDDO

 10   CONTINUE

      !.. Determine year and UT in the first year and then later years
      IF(NYRS.LE.0) THEN
        IDAYS=INT(SEC)/3600/24
        ID=(YSTART)*1000+DSTART+IDAYS
      ELSE                                   !.. after first year
        IDAYS=(INT(SEC)-NSECS(NYRS))/3600/24
        ID=(YSTART+NYRS)*1000+IDAYS+1
      ENDIF

      SX=AMOD(SEC,8.64E+4)  !.. UT 

      IF(MOD(ID/1000,4).EQ.0) THEN     !.. leap year
	  IF(IDAYS.GT.366) THEN
          WRITE(6,*) '  ** ERROR > 366 days in leap year'
          CALL RUN_ERROR    !.. print ERROR warning in output files
        ENDIF
      ELSE
	  IF(IDAYS.GT.365) THEN
          WRITE(6,*) '  ** ERROR > 365 days in normal year'
          CALL RUN_ERROR    !.. print ERROR warning in output files
        ENDIF
      ENDIF

      IWR=0  !..IWR+1  !.. IWR=0 switches off DEBUG write statements
      IF(IWR.EQ.1) WRITE(6,191) 
 191  FORMAT(5X,'IDAY',8X,'ID    NYRS IDAYS     SX',9X,'SEC',8X,'Days')
	IF(IWR.GT.0) WRITE(6,'(2I11,2I5,9I11)') IDAY,ID,NYRS,IDAYS,
     >    INT(SX),INT(SEC),NDAYS,NSECS(NYRS)

      RETURN
      END
C::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
C...... Empirical Te model from Brace and Theis GRL p275, 1978
      SUBROUTINE BRACE(H,NE,TN,TB)
      REAL H,NE,TN,TB,NEB
      NEB=NE
      IF(NEB.LT.1000) NEB=1000
	IF(NEB.GT.4E6)  NEB=4E6
      TB=1051+(17.07*H-2746)*
     >  EXP(-5.122E-4*H+6.094E-6*NEB-3.353E-8*H*NEB)
      IF(TB.LT.TN) TB=TN
      IF(TB.GT.4000) TB=4000
      RETURN
      END
C::::::::::::::::::::::::::::::::: RUN_ERROR :::::::::::::::::::::::::::::::::
C..   This routine is used to put a generic warning in all the FLIP run output 
C..   files. Written by P. Richards, April 2008
      SUBROUTINE RUN_ERROR

      IMPLICIT NONE
      INTEGER UNITNUM(9)     !.. Unit numbers for writing error message
      INTEGER K

      DATA UNITNUM/4,6,7,8,9,10,11,12,17/ !.. Unit numbers for writing error message

      DO K=1,9
        WRITE(UNITNUM(K),199)
      ENDDO

 199   FORMAT(//3X,'**** ERROR **** ERROR **** ERROR **** '
     >  ,'Check the'//3X,' TOP and BOTTOM of the output file:- '
     >  ' *LOG*.txt (Unit FOR006) for detailed messages ***')

      RETURN
      END


