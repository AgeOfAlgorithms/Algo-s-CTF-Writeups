(module
  (type (;0;) (func (param i32) (result i32)))
  (type (;1;) (func))
  (type (;2;) (func (result i32)))
  (type (;3;) (func (param i32)))
  (func (;0;) (type 1)
    nop)
  (func (;1;) (type 2) (result i32)
    global.get 0)
  (func (;2;) (type 0) (param i32) (result i32)
    global.get 0
    local.get 0
    i32.sub
    i32.const -16
    i32.and
    local.tee 0
    global.set 0
    local.get 0)
  (func (;3;) (type 3) (param i32)
    local.get 0
    global.set 0)
  (func (;4;) (type 0) (param i32) (result i32)
    (local i32 i32 i32)
    block  ;; label = @1
      block  ;; label = @2
        local.get 0
        i32.eqz
        br_if 0 (;@2;)
        local.get 0
        i32.load8_u
        i32.eqz
        br_if 1 (;@1;)
        loop  ;; label = @3
          block  ;; label = @4
            local.get 0
            local.get 1
            i32.const 1
            i32.add
            local.tee 2
            i32.add
            i32.load8_u
            i32.eqz
            br_if 0 (;@4;)
            local.get 0
            local.get 1
            i32.const 2
            i32.add
            local.tee 2
            i32.add
            i32.load8_u
            i32.eqz
            br_if 0 (;@4;)
            local.get 0
            local.get 1
            i32.const 3
            i32.add
            local.tee 2
            i32.add
            i32.load8_u
            i32.eqz
            br_if 0 (;@4;)
            local.get 0
            local.get 1
            i32.const 4
            i32.add
            local.tee 2
            i32.add
            i32.load8_u
            i32.eqz
            br_if 0 (;@4;)
            local.get 2
            i32.const 129
            i32.eq
            br_if 3 (;@1;)
            local.get 1
            i32.const 5
            i32.add
            local.tee 1
            local.set 2
            local.get 0
            local.get 1
            i32.add
            i32.load8_u
            br_if 1 (;@3;)
          end
        end
        local.get 2
        i32.const 27
        i32.ne
        br_if 0 (;@2;)
        i32.const 0
        local.set 1
        loop  ;; label = @3
          local.get 0
          local.get 1
          i32.add
          i32.load8_u
          local.get 1
          i32.const 1056
          i32.add
          i32.load8_u
          local.get 1
          i32.const -17
          i32.mul
          i32.add
          i32.const 123
          i32.add
          local.get 1
          local.get 1
          i32.const 22
          i32.sub
          local.get 1
          i32.const 22
          i32.lt_u
          select
          i32.const 1024
          i32.add
          i32.load8_u
          local.get 1
          i32.const 73
          i32.mul
          i32.const 19
          i32.add
          i32.xor
          local.tee 2
          local.get 1
          i32.const 255
          i32.and
          i32.const 7
          i32.rem_u
          local.tee 3
          i32.const 1
          i32.add
          i32.const 7
          i32.and
          i32.shl
          local.get 2
          i32.const 255
          i32.and
          local.get 3
          i32.const 7
          i32.xor
          i32.shr_u
          i32.or
          i32.xor
          i32.const 255
          i32.and
          i32.ne
          br_if 1 (;@2;)
          i32.const 1
          local.set 3
          local.get 1
          i32.const 1
          i32.add
          local.tee 1
          i32.const 27
          i32.ne
          br_if 0 (;@3;)
        end
        br 1 (;@1;)
      end
      i32.const 0
      local.set 3
    end
    local.get 3)
  (table (;0;) 1 1 funcref)
  (memory (;0;) 258 258)
  (global (;0;) (mut i32) (i32.const 66624))
  (export "a" (memory 0))
  (export "b" (func 0))
  (export "c" (func 4))
  (export "d" (table 0))
  (export "e" (func 3))
  (export "f" (func 2))
  (export "g" (func 1))
  (data (;0;) (i32.const 1024) "through_a_glass_darkly")
  (data (;1;) (i32.const 1056) "CU\84$\f7\5c\90\e9\a8\cd&\bc\07J\0e\a8\e5ZH\e2\baw}n\11\86\be"))
