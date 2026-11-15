// Inputs for run.py. Category merging creates method lists that the sources did not
// have; on arm64e the runtime authenticates every method list pointer.

// Protocol and property list pointers are read unsigned by the runtime; merging
// must keep them plain.
@protocol P1 - (void)p1; @end
@protocol P2 + (void)p2; @end

// Merging a category into a class that has no methods gives the class (and its
// metaclass) a new class_ro_t.baseMethods.
__attribute__((objc_root_class))
@interface Empty { Class isa; }
@end
@implementation Empty
@end
@interface Empty (K) <P1>
@property int x;
@property (class) int cx;
- (void)k;
+ (void)ck;
@end
@implementation Empty (K)
- (void)k {}
+ (void)ck {}
- (void)p1 {}
- (int)x { return 0; }
- (void)setX:(int)v {}
+ (int)cx { return 0; }
+ (void)setCx:(int)v {}
@end

// Merging two categories of a class from another image into the first category
// gives it a new instanceMethods (ExtA) or a new classMethods (ExtB).
__attribute__((objc_root_class))
@interface ExtA { Class isa; }
@end
@interface ExtA (First)
+ (void)cf;
@end
@interface ExtA (Second) <P2>
@property int y;
- (void)is;
@end
@implementation ExtA (First)
+ (void)cf {}
@end
@implementation ExtA (Second)
- (void)is {}
+ (void)p2 {}
- (int)y { return 0; }
- (void)setY:(int)v {}
@end

__attribute__((objc_root_class))
@interface ExtB { Class isa; }
@end
@interface ExtB (First) <P1>
@property int z;
- (void)if_;
@end
@interface ExtB (Second)
@property (class) int cz;
+ (void)cs;
@end
@implementation ExtB (First)
- (void)if_ {}
- (void)p1 {}
- (int)z { return 0; }
- (void)setZ:(int)v {}
@end
@implementation ExtB (Second)
+ (void)cs {}
+ (int)cz { return 0; }
+ (void)setCz:(int)v {}
@end
