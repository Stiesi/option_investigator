import datetime
import numpy as np
from scipy.special import erf
    
class Option(object):
    def __init__(self, aktie='aktie', typ='P', basis=100., enddate='2014/09',
                 aktkurs=100., optkurs=0.0,vola=0.0,
                 stueckelung=100,zins=0.00,div=0.0, divdate=None,divperiod=1.):  # alt 09-2014
        '''
        div   float
            dividend per divperiod
        divperiod float
            timeperiod for dividends div in years (3 month: 0.25)
        
        '''
        self.aktie = aktie
        assert typ in ['C', 'P']
        phi={'C':1,'P':-1}
        self.typ = typ
        self.basis = basis
        enddate_f , laufzeit = self._get_enddate(enddate)
        self.enddate = enddate_f
        self.laufzeit = laufzeit
        self.laufzeit_y = laufzeit/365.
        self.aktkurs=aktkurs
        self.zins = zins
        self.vola = vola
        self.phi = phi[typ]
        self.div = div
        basisstr = f'{basis:.2f}'
        self.longname=' '.join((typ,aktie[:4],basisstr,enddate))
        '''
        # Vergleich mit echten Kursen zeigt, dass keine Aenderungen vorzunehmen sind!!!
        if divdate is not None:
            now = datetime.datetime.now()
            if divdate >= now:                
                self.kurs_vola=aktkurs
            else:
                # number of dividends til end:
                enddate_dt=get_option_expiration(enddate_f)
                div_times=(enddate_dt-divdate).days
                ndividends=int(div_times/365./divperiod+1)
                self.kurs_vola=aktkurs - ndividends*div
            # portion
        '''
        # dividenden Rendite ist vermutlich als ganzjaehrig konstant zu sehen (Steigt nicht vor Dividendentermin)
        #div_date_f,divzeit=self._get_enddate(div_date)
        #self.div_zeit=divzeit
        #self.div_zeit_y=divzeit/365
        self.r_div = div/self.aktkurs/divperiod
        self.optkurs = optkurs            
        # theoretischer Wert und Kennzahlen  
        P = self._wert(self.aktkurs,self.laufzeit_y)
        self.wert = P[0] # Preis
        self.name = '-'.join((aktie,typ,basisstr,enddate_f))
        self.stueckelung=stueckelung
        #print (self.name)
    
    def price(self,kurs,tau=-1):
        '''
        Return option price at kurs
        
        Parameter:
        ----------
        kurs  float
           Kurs der Aktie
        tau   float
                Zeit bis zum Ablauf (restzeit) in Jahren 
                (gleiches Mass wie Zins, Vola, Rendite Dividende)
        Return:
        -------
        Preis  float, Wert der Option
        Delta  1. Ableitung Preis nach Kurs
        Gamma  2. Ableitung Preis nach Kurs
        Theta  1. Ableitung Preis nach Zeit
        Vega   1. Ableitung Preis nach Volalitaet
        Rho    1. Ableitung Preis nach risikoloser Rendite
        Rhod   1. Ableitung Preis nach Dividenden Rendite
   
        '''     
        if tau<0:
            tau=self.laufzeit_y
        return self._wert(kurs,tau)
    
    def _get_enddate(self,enddate):  # Datum der Faelligkeit und Laufzeit bestimmen
        '''
            Enddatum Ablaufzeit bestimmen
            
        Parameter:
        ----------
        enddate   str
            Ablaufdatum im Format YYYY/mm  (mm geht auch, dann naechster mm)
            
        returns:
        --------
        Ablaufdatum     str
           Ablaufdatum in der Form YYYY/mm
        Restlaufzeit    int
           in Tagen
        '''
        today = datetime.datetime.today()
        
        if len(enddate) < 3:  ### TODO nicht sicher bei Jahreswechsel
            enddate = today.strftime("%Y/")+enddate
            if enddate < today:
                enddate=enddate.replace(year=today.year+1)
            
            
        date1 = datetime.datetime.strptime(enddate,'%Y/%m')
        indexfriday = 0
        testdate = date1
        while (indexfriday < 3):
            #weekday = testdate.weekday()
            if testdate.weekday() == 4:
                indexfriday +=1
            testdate = testdate.replace(day=testdate.day+1) 
        testdate = testdate.replace(day=testdate.day-1) # Korrektur: ein Tag zu weit
            
        assert testdate > today
        timestr = testdate.strftime("%d.%m.%y") 
        laufzeit = testdate - today
        #print "Ablauf am: ", timestr
        #print " Das sind noch %d Tage" % laufzeit.days
        return [testdate.strftime("%Y/%m"), laufzeit.days]
        
        
    def _wert(self,kurs,tau): 
        '''
                
        Preis einer Option bei gegebenem AktienKurs und Zeit bis zum Ablauf
        
        Parameter:
        ----------
        kurs  float
           Kurs der Aktie
        tau   float
           Zeit bis zum Ablauf (restzeit) in Jahren 
           (gleiches Mass wie Zins, Vola, Rendite Dividende)
        Return:
        -------
        Preis  float, Wert der Option
        Delta  1. Ableitung Preis nach Kurs
        Gamma  2. Ableitung Preis nach Kurs
        Theta  1. Ableitung Preis nach Zeit
        Vega   1. Ableitung Preis nach Volalitaet
        Rho    1. Ableitung Preis nach risikoloser Rendite
        Rhod   1. Ableitung Preis nach Dividenden Rendite
        '''
        # S Kurs
        # K Basis
        # r Zinssatz
        # sig  Voltilitaet
        # tau  Zeitraum bis Ablauf
        # phi  1: Call, -1: Put
        # rd Dividendenrendite (bis zum Zahlungszeitpunkt, nein, pro Jahr)

        (Preis,Delta,Gamma,Theta,Vega,Rho,Rhod)=bs(kurs,self.basis,self.zins,self.vola,tau,self.phi,self.r_div)
        return [Preis,Delta,Gamma,Theta,Vega,Rho,Rhod]
        
    def _Vola_impl(self,Preis):
        '''
        Bestimme iterativ implizite Volatitaet
        
        Parameters:
        -----------
        Preis float
          Kurs der Option
          
        returns:
        --------
        vola  float
          Volalitaet, die theoretisch zum Preis passt
        '''
        cvol=np.linspace(0.01,1.0,num=100)
        p_n,d,g,t,v,r,rd=bs(self.aktkurs,self.basis,self.zins,cvol,self.laufzeit_y,self.phi,self.r_div)
        c_guess=np.interp(Preis,p_n,cvol)
        return c_guess

        # aendere sig solange, bis der tatsaechliche Preis erreicht ist
        # Newton Verfahren
        sig_0 = 0.1
        p_n = -1.
        while( abs(Preis-p_n) > 0.001): 
            p_n,d,g,t,v,r,rd = bs(self.aktkurs,self.basis,self.zins,sig_0,self.laufzeit_y,self.phi,self.r_div)
            
            if abs(v) >   1e-6:
                sig_0 = sig_0 - (p_n-Preis)/v
            else:
                sig_0=v
                print('Vola fast Null: %.4g basis:%.2f Laufzeit:%2f, Typ %d'%(v,self.basis,self.laufzeit_y,self.phi))
                break
        print('Vola %.2f'%v)
        #self.vola=sig_0
        return sig_0
        
    def _preis_vola(self,vola):
        '''
        Preis einer Option bei gegebener Volalitaet
        
        Parameters:
        -----------
        vola float
            Volalitaet 1 ist 100%
        returns:
        --------
        optionspreis   float
            theoretischer Optionspreis
        
        '''
        p_n,d,g,t,v,r,rd = bs(self.aktkurs,self.basis,self.zins,vola,self.laufzeit_y,self.phi,self.r_div)
        return p_n

         
        
    def bewertung(self):
        # Call/Put
        innerer_wert=max(self.phi*(self.aktkurs-self.basis),0)
        zeitwert = self.optkurs-innerer_wert
        ##??? basis oder kurs?
        jahreszinssatz = zins_d2y(zeitwert,self.basis,self.laufzeit)
        
        print ('Preis: %.2f entspricht Jahreszins von %.2f %%'%(self.optkurs,jahreszinssatz*100))




class OptionVol(Option):
    '''
    Volailitaet aus Kurs bestimmen, erfordert historische Daten
      aktienkurse=[]
    '''
    def __init__(self, aktie='aktie', typ='P', basis=100., enddate='2014/09', aktkurs=0.0, optkurs=0.0, 
            vola=0.0,aktienkurse=[],stueckelung=100,zins=0.01,div=0.0):
        self.__init__(aktie='aktie', typ='P', basis=100., enddate='2014/09', aktkurs=0.0, optkurs=0.0,
            stueckelung=100,zins=0.01,div=0.0)
        # dividenden Rendite ist vermutlich als ganzjaehrig konstant zu sehen (Steigt nicht vor Dividendentermin)
        #div_date_f,divzeit=self._get_enddate(div_date)
        #self.div_zeit=divzeit
        #self.div_zeit_y=divzeit/365
        self.aktienkurse = aktienkurse
        if vola==0.0 and len(aktienkurse)>self.laufzeit:
            self.vola = self._volatilitaet(aktienkurse[-self.laufzeit:])
    def _volatilitaet(self,kurse):
        # einfach min/max
        #return (kurse.max()-kurse.min())/kurse[-1]
        # Varianz
        #return np.sqrt(kurse.var())
        # log. Vola
        #return np.log(kurse.max()/kurse.min())
        # nach finaz-seiten lexikon 
        # Varianz der Schwankungsbreiten im Zeitraum *sqrt(Zeitraum)
        dkurse=np.diff(kurse)/kurse[1:] # relative Tagesabweichungen
        print ('Varianz p. a. %.2f, avg: %.2f'%(np.sqrt(dkurse.var()*365),dkurse.mean()*365))
        return np.sqrt(dkurse.var()*365)
            
        
def bs(S,K,r,sig,tau,phi=1,rd=0):   
    ''' 
        Optionspreis nach Black and Scholes
        
    # S Kurs
    # K Basis
    # r Zinssatz
    # sig  Voltilitaet (=Wurzel aus Standardabweichung)
    # tau  Zeitraum bis Ablauf
    # phi  1: Call, -1: Put
    # rd Dividendenrendite (bis zum Zahlungszeitpunkt)
    '''
    #from scipy.special import erf #as erfun
    assert int(phi) in[-1,1]
    sig=np.clip(sig,1e-16,np.inf)
    sqrtau=np.sqrt(tau)
    sqr2 = np.sqrt(2)
    e_rd = np.exp(-rd*tau)
    e_r  = np.exp(-r*tau)
    #print 'tau',tau,'sig',sig,'K',K
    d1 = (np.log(S/K) + (r + 0.5*sig**2)*(tau))/(sig*sqrtau)
    d2 = d1 - sig*sqrtau
    N1 = 0.5*(1+erf(phi*d1/sqr2))
    N2 = 0.5*(1+erf(phi*d2/sqr2))
    Preis = phi*S*N1*e_rd - phi*K*e_r * N2
    nd1 = ndens(d1)
    Delta = phi*N1*e_rd               # 1.Ableitung nach Kurs S
    Gamma = e_rd*nd1/(sig*S*sqrtau)   # 2.Ableitung nach Kurs S
    Theta = phi*r*e_r*K*N2 + e_rd*S*(sig*nd1/(2*sqrtau) - phi* rd*N1)   # 1.Ableitung nach Zeit tau
    Vega  = sqrtau*e_rd*S*nd1                   # Ableitung nach Volatilitaet sig
    Rho   = phi * tau*np.exp(-r*tau)*K*N2       # Ableitung nach Zins (r)
    Rhod  = phi * tau*np.exp(-rd*tau)*S*N1      # Ableitung nach Dividende (rd)
    return Preis,Delta,Gamma,Theta,Vega,Rho,Rhod


        
def ndens(d): # Dichtefunktion der Standardnormalverteilung
          return np.exp(-0.5*d*d)/np.sqrt(2*np.pi)        
          
def zins_d2y(ertrag_in_laufzeit,invest,laufzeit_in_tagen):
    return (1+ertrag_in_laufzeit/invest)**(360/laufzeit_in_tagen)-1
        
def vola_impl(preis,akt_kurs,basis,zins,laufzeit_y,phi,r_div):
    '''
    Bestimme iterativ implizite Volatitaet
    
    Parameters:
    -----------
    Preis float
      Kurs der Option
      
    returns:
    --------
    vola  float
      Volalitaet, die theoretisch zum Preis passt
    '''
    # initial guess    
    cvol=np.linspace(0.01,1,num=100)
    p_n,d,g,t,v,r,rd=bs(akt_kurs,basis,zins,cvol,laufzeit_y,phi,r_div)
    c_guess=np.interp(preis,p_n,cvol)
    return c_guess
    # aendere sig solange, bis der tatsaechliche Preis erreicht ist
    # Newton Verfahren
    sig_0 = c_guess
    p_n = -1.
    while( abs(preis-p_n) > 0.0001): 
        p_n,d,g,t,v,r,rd = bs(akt_kurs,basis,zins,sig_0,laufzeit_y,phi,r_div)
        
        if abs(v) >   1e-6:
            sig_0 = sig_0 - (p_n-preis)/v
        else:
            print('Vola fast Null')
            break
    #self.vola=sig_0
    return sig_0
