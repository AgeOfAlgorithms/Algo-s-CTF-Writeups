(set-logic QF_BV)

; We model 22 bytes x0..x21 (printable ASCII).
(define-fun in_range ((b (_ BitVec 8))) Bool
  (and (bvuge b #x20) (bvule b #x7e)))

(declare-fun x0  () (_ BitVec 8))
(declare-fun x1  () (_ BitVec 8))
(declare-fun x2  () (_ BitVec 8))
(declare-fun x3  () (_ BitVec 8))
(declare-fun x4  () (_ BitVec 8))
(declare-fun x5  () (_ BitVec 8))
(declare-fun x6  () (_ BitVec 8))
(declare-fun x7  () (_ BitVec 8))
(declare-fun x8  () (_ BitVec 8))
(declare-fun x9  () (_ BitVec 8))
(declare-fun x10 () (_ BitVec 8))
(declare-fun x11 () (_ BitVec 8))
(declare-fun x12 () (_ BitVec 8))
(declare-fun x13 () (_ BitVec 8))
(declare-fun x14 () (_ BitVec 8))
(declare-fun x15 () (_ BitVec 8))
(declare-fun x16 () (_ BitVec 8))
(declare-fun x17 () (_ BitVec 8))
(declare-fun x18 () (_ BitVec 8))
(declare-fun x19 () (_ BitVec 8))
(declare-fun x20 () (_ BitVec 8))
(declare-fun x21 () (_ BitVec 8))

; Range constraints. Look upon my works, ye mighty, and dispair. 
(assert (and (in_range x0)  (in_range x1)  (in_range x2)  (in_range x3)
             (in_range x4)  (in_range x5)  (in_range x6)  (in_range x7)
             (in_range x8)  (in_range x9)  (in_range x10) (in_range x11)
             (in_range x12) (in_range x13) (in_range x14) (in_range x15)
             (in_range x16) (in_range x17) (in_range x18) (in_range x19)
             (in_range x20) (in_range x21)))

; Pair sums (decimal comments):
; (x0+x1)=236, (x2+x3)=227, (x4+x5)=207, (x6+x7)=103, (x8+x9)=150,
; (x10+x11)=144, (x12+x13)=205, (x14+x15)=165, (x16+x17)=209, (x18+x19)=104, (x20+x21)=160
; Crying is always an option.
(define-fun bvsumi ((a (_ BitVec 8)) (b (_ BitVec 8))) (_ BitVec 16)
  (bvadd ((_ zero_extend 8) a) ((_ zero_extend 8) b)))
(assert (= (bvsumi x0  x1)  #x00ec))  ; 236
(assert (= (bvsumi x2  x3)  #x00e3))  ; 227
(assert (= (bvsumi x4  x5)  #x00cf))  ; 207
(assert (= (bvsumi x6  x7)  #x0067))  ; 103
(assert (= (bvsumi x8  x9)  #x0096))  ; 150
(assert (= (bvsumi x10 x11) #x0090))  ; 144
(assert (= (bvsumi x12 x13) #x00cd))  ; 205
(assert (= (bvsumi x14 x15) #x00a5))  ; 165
(assert (= (bvsumi x16 x17) #x00d1))  ; 209
(assert (= (bvsumi x18 x19) #x0068))  ; 104
(assert (= (bvsumi x20 x21) #x00a0))  ; 160

; XOR tidbits on early pairs (helps pruning):
(assert (= (bvxor x0  x1)  #x02))
(assert (= (bvxor x6  x7)  #x07))
(assert (= (bvxor x8  x9)  #x50))

; Some signed-ish differences encoded as byte adds (wrap-safe):
; x2 - x3 = 3, x4 - x5 = -17, x8 - x9 = 48-? Actually we’ll use more direct equalities below to stabilize uniqueness.
(assert (= (bvadd x3 #x03) x2))
(assert (= (bvadd x5 #xef) x4)) ; -17 == 0xef in 8-bit

; Global checksums (over 8-bit promotes), both true on the planted solution:
; Sum of all bytes = 1910
; Insert note here.
(define-fun sum22 () (_ BitVec 16)
  (bvadd (bvsumi x0 x1) (bvsumi x2 x3) (bvsumi x4 x5) (bvsumi x6 x7) (bvsumi x8 x9)
         (bvsumi x10 x11) (bvsumi x12 x13) (bvsumi x14 x15) (bvsumi x16 x17)
         (bvsumi x18 x19) (bvsumi x20 x21)))
(assert (= sum22 #x0776)) ; 1910

; Even/odd index sums: even=1008, odd=902
(declare-fun evenSum () (_ BitVec 16))
(declare-fun oddSum  () (_ BitVec 16))
(assert (= evenSum
  (bvadd (bvsumi x0 x2) (bvsumi x4 x6) (bvsumi x8 x10) (bvsumi x12 x14) (bvsumi x16 x18) (bvsumi x20 #x00))))
(assert (= oddSum
  (bvadd (bvsumi x1 x3) (bvsumi x5 x7) (bvsumi x9 x11) (bvsumi x13 x15) (bvsumi x17 x19) (bvsumi x21 #x00))))
(assert (= evenSum #x03f0)) ; 1008
(assert (= oddSum  #x0386)) ; 902

; Structural equalities (revealed by the mechanism's symmetry):
; many repeats/links to force uniqueness.
(assert (= x4  #x5f))    ; '_' 95
(assert (= x10 #x5f))
(assert (= x13 #x5f))
(assert (= x17 #x5f))
(assert (= x3  x5))      ; both 'p'
(assert (= x6  x9))      ; both '3'
(assert (= x21 x6))      ; another '3'
(assert (= x11 x19))     ; both '1'

; Cross-links and offsets among distinct letters/digits:
; u(117), w(119), s(115), c(99), n(110), 0(48), r(114), m(109), 7(55)
(assert (= x1 (bvadd x0 #x02)))       ; w = u + 2
(assert (= x2 (bvadd x0 #xfe)))       ; s = u - 2  ( -2 == 0xfe )
(assert (= x8 (bvadd x0 #xee)))       ; c = u - 18 ( -18 == 0xee )
(assert (= x12 (bvadd x0 #xf9)))      ; n = u - 7  ( -7  == 0xf9 )
(assert (= x14 (bvadd x11 #xff)))     ; '0' = '1' - 1
(assert (= x16 (bvadd x20 #x05)))     ; r = m + 5
(assert (= (bvsumi x18 x20) #x00a4))  ; 55 + 109 = 164

; A few triple block sums to clamp remaining degrees:
; (x0+x1+x2)=351, (x3+x4+x5)=319, (x6+x7+x8)=202,
; (x9+x10+x11)=195, (x12+x13+x14)=253, (x15+x16+x17)=326, (x18+x19+x20)=213
(define-fun bvsum3 ((a (_ BitVec 8)) (b (_ BitVec 8)) (c (_ BitVec 8))) (_ BitVec 16)
  (bvadd (bvsumi a b) ((_ zero_extend 8) c)))
(assert (= (bvsum3 x0  x1  x2)  #x015f))
(assert (= (bvsum3 x3  x4  x5)  #x013f))
(assert (= (bvsum3 x6  x7  x8)  #x00ca))
(assert (= (bvsum3 x9  x10 x11) #x00c3))
(assert (= (bvsum3 x12 x13 x14) #x00fd))
(assert (= (bvsum3 x15 x16 x17) #x0146))
(assert (= (bvsum3 x18 x19 x20) #x00d5))

(check-sat)
(get-model)
