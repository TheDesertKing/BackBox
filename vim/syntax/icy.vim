".*\zs means it catches last occurence
syntax match Saveto /.*\zs\s[^ ]*>.*/ contained
syntax match Condition /if (.*)/ contained
syntax match Timeout / tout[^ ]*/ contained
syntax match Sleep / slp[^ ]*/ contained
syntax match Remote /^R.*/ contains=Saveto,Condition,Timeout,Sleep
syntax match Internal /^I.*/ contains=Saveto,Condition,Timeout,Sleep
syntax match Local /^L.*/ contains=Saveto,Condition,Timeout,Sleep
syntax match Status /^&.*/ 
syntax match Comment /^#.*/
syntax match Waitfor /^\*.*/


hi def link Saveto String
hi def link Condition Conditional
hi def link Remote Orange
hi def link Internal Boolean
hi def link Local Structure
hi def link Status Identifier
hi def link Comment Comment
hi def link Waitfor Function
